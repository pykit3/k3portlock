"""
k3portlock is a cross-process lock that is implemented with socket binding.
No two sockets can bind the same address, so whoever binds the address of a key
holds the lock of that key.

On Linux, the address is the abstract Unix socket `/portlock/<key>`.
Only processes in the same network namespace share these locks.
A container with its own network does not see the locks of the host.

On other systems, k3portlock hashes the key to one of 20000 base ports in
`[40000, 60000)`.
k3portlock tries to bind **3** ports from the base port on loopback ip `127.0.0.1`.
If a Portlock instance succeeds on binding **2** ports out of 3,
it is considered this instance has acquired the lock.
Two different keys whose base ports are less than 3 apart can block each other,
and so can other programs that bind these ports.
With 100 keys in use at once, about one pair of keys is that close.
A collision looks like a lock held by another process.
`try_lock()` returns `False`, and `acquire()` raises `PortlockTimeout` unless the
other lock is released in time.

A lock lives as long as its socket.
`release()` or the exit of the process closes the socket and frees the lock,
so a killed process never leaves a stale lock.

"""

from .portlock import (
    Portlock,
    PortlockError,
    PortlockTimeout,
)

__all__ = [
    "Portlock",
    "PortlockError",
    "PortlockTimeout",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3portlock")
