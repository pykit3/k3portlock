import errno
import hashlib
import itertools
import os
import resource
import threading
import time
import unittest
from unittest import mock

import k3ut

import k3portlock

dd = k3ut.dd


class FakeSocket:
    # bind() fails with the errno that errs gives for the address.

    def __init__(self, errs):
        self.errs = errs

    def bind(self, addr):
        err = self.errs.get(addr)
        if err is None:
            return
        raise OSError(err, os.strerror(err))

    def close(self):
        pass


def try_lock_in_thread(lock):
    # The thread lock of an instance is re-entrant, so only another thread shows whether the instance is free.
    rst = []

    def worker():
        rst.append(lock.try_lock())
        lock.release()

    th = threading.Thread(target=worker)
    th.start()
    th.join()
    return rst[0]


class TestPortlock(unittest.TestCase):
    def test_mem_test(self):
        a = k3portlock.Portlock("k1")
        b = k3portlock.Portlock("k1")

        dd("lock-a: ", a.addr)
        dd("lock-b: ", b.addr)

        r = b.has_locked()
        self.assertFalse(r, "not locked")

        r = b.has_locked()
        self.assertFalse(r, "still not locked")

        a.acquire()

        r = b.has_locked()
        self.assertFalse(r, "not locked by me.")

        r = b.try_lock()
        self.assertFalse(r, "can not lock while another one hold it")

        b.release()
        r = b.try_lock()
        self.assertFalse(r, "b can not release lock belongs to a")

        a.release()

        r = b.try_lock()
        self.assertTrue(r, "I can hold it now")
        dd("try-locked:", r)

        try:
            a.acquire()
            self.fail("lock-a should not be able to get lock")
        except k3portlock.PortlockError:
            pass

    def test_1_lock_per_thread(self):
        sess = {"n": 0}

        def worker(lock, ident):
            for ii in range(1000):
                lock.acquire()
                dd(f"{ident}-{ii} start")

                self.assertEqual(0, sess["n"], "n is 0 just after lock is acquired, 1-lock-for-1")

                sess["n"] += 1
                time.sleep(0.001)
                self.assertEqual(1, sess["n"], "no more than 2 thread holding lock")
                sess["n"] -= 1
                dd(f"{ident}-{ii} end")
                lock.release()

        ts = [threading.Thread(target=worker, args=(k3portlock.Portlock("x", timeout=100), x)) for x in range(10)]

        for t in ts:
            t.start()

        for t in ts:
            t.join()

    def test_1_lock_for_all_thread(self):
        sess = {"n": 0}

        def worker(lck):
            for ii in range(1000):
                lck.acquire()

                self.assertEqual(0, sess["n"], "n is 0 just after lock is acquired, 1-lock-for-all")

                sess["n"] += 1
                time.sleep(0.001)
                self.assertEqual(1, sess["n"], "no more than 2 thread holding lock")
                sess["n"] -= 1
                lck.release()

        lock = k3portlock.Portlock("x", timeout=100)
        ts = [threading.Thread(target=worker, args=(lock,)) for x in range(3)]

        for t in ts:
            t.daemon = True
            t.start()

        for t in ts:
            t.join()

    def test_shared_instance_timeout(self):
        # One instance is shared by threads: a thread waiting for another one's lock still times out.
        lock = k3portlock.Portlock("shared-timeout", timeout=0.1)
        held = threading.Event()
        done = threading.Event()

        def holder():
            with lock:
                held.set()
                done.wait(5)

        th = threading.Thread(target=holder)
        th.start()
        held.wait()

        t0 = time.monotonic()
        with self.assertRaises(k3portlock.PortlockTimeout):
            lock.acquire()
        spent = time.monotonic() - t0

        self.assertFalse(lock.try_lock())

        done.set()
        th.join()

        self.assertLess(spent, 1)

    def test_majority_of_ports(self):
        # On a system other than Linux, the lock needs 2 of its 3 ports, and another program can hold any of them.
        lock = k3portlock.Portlock("majority")
        ip, port = lock.addr
        cases = (
            ((), True),
            ((0,), True),
            ((1,), True),
            ((2,), True),
            ((0, 1), False),
            ((0, 2), False),
            ((1, 2), False),
            ((0, 1, 2), False),
        )

        with mock.patch.object(k3portlock.portlock, "OS", "Darwin"):
            for busy, expected in cases:
                dd("busy ports:", busy)
                errs = {(ip, port + i): errno.EADDRINUSE for i in busy}
                with mock.patch("socket.socket", return_value=FakeSocket(errs)):
                    rst = lock.try_lock()
                    self.assertEqual(expected, rst)
                    self.assertEqual(expected, lock.has_locked())
                    lock.release()

            # No failed attempt keeps the instance.
            with mock.patch("socket.socket", return_value=FakeSocket({})):
                self.assertTrue(try_lock_in_thread(lock))

    def test_bind_error(self):
        # A bind error other than EADDRINUSE propagates, and the failed attempt does not keep the instance.
        lock = k3portlock.Portlock("bind-error")
        ip, port = lock.addr
        cases = (
            ("Linux", "\0/portlock/bind-error"),
            ("Darwin", (ip, port + 1)),
        )

        for os_name, addr in cases:
            dd("OS:", os_name)
            with mock.patch.object(k3portlock.portlock, "OS", os_name):
                fake = FakeSocket({addr: errno.EACCES})
                with mock.patch("socket.socket", return_value=fake), self.assertRaises(OSError) as ctx:
                    lock.try_lock()

                self.assertEqual(errno.EACCES, ctx.exception.errno)
                self.assertFalse(lock.has_locked())

                with mock.patch("socket.socket", return_value=FakeSocket({})):
                    self.assertTrue(try_lock_in_thread(lock))

    def test_acquire_ignores_wall_clock(self):
        # A wall clock that jumps forward between two attempts does not end the wait.
        lock = k3portlock.Portlock("wall-clock", timeout=5)
        lock.try_lock = mock.Mock(side_effect=[False, True])

        with mock.patch("time.time", side_effect=itertools.count(0, 1000)):
            lock.acquire()

        self.assertEqual(2, lock.try_lock.call_count)

    def test_sleep_time(self):
        lock0 = k3portlock.Portlock("x")
        lock = k3portlock.Portlock("x", timeout=1, sleep_time=2)

        with lock0:
            t0 = time.time()
            try:
                lock.acquire()
            except k3portlock.PortlockTimeout:
                pass

            t1 = time.time()

            self.assertTrue(
                0.9 < t1 - t0 < 1.1,
                f"sleep_time should not affect timeout(1 sec), but it spends {t1 - t0} seconds",
            )

    # Outside Linux each lock binds 2 of the 20000 ports in PORT_RANGE, so at most about 10000 locks exist together.
    @unittest.skipUnless(k3portlock.portlock.OS == "Linux", "1 << 15 locks fit only in Linux abstract Unix sockets")
    def test_collision(self):
        n_lock = 1 << 15

        # Each lock holds one socket, and the rest of the process needs some more files.
        n_file = n_lock + 1024
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if hard < n_file:
            self.skipTest(f"{n_file} open files are needed, but RLIMIT_NOFILE allows only {hard}")

        # A process may raise its soft limit up to its hard limit without privileges.
        new_soft = max(soft, n_file)
        resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))

        dd = {}
        ls = []
        collision_num = 0
        for i in range(n_lock):
            key = str(hashlib.sha1(str(i).encode("utf8")).hexdigest())
            lck = key
            lock = k3portlock.Portlock(lck, timeout=8)
            r = lock.try_lock()
            if r:
                dd[lock.addr] = i
                ls.append(lock)
            else:
                collision_num += 1
        self.assertTrue(
            (collision_num / n_lock) < 0.01, "The lock collision rate should be less than the threshold of 1%"
        )
