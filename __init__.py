"""
k3portlock is a cross-process lock that is implemented with `tcp` port binding.
Since no two processes could bind on a same TCP port.

k3portlock tries to bind **3** ports on loopback ip `127.0.0.1`.
If a Portlock instance succeeds on binding **2** ports out of 3,
it is considered this instance has acquired the lock.

"""

# from .proc import CalledProcessError
# from .proc import ProcError

__version__ = "0.1.2"
__name__ = "k3portlock"

from .portlock import (
    PortlockError,
    PortlockTimeout,
    Portlock,
)

__all__ = [
    'PortlockError',
    'PortlockTimeout',
    'Portlock',
]
