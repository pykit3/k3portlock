# k3portlock

[![Action-CI](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/k3portlock/badge/?version=stable)](https://k3portlock.readthedocs.io/en/stable/?badge=stable)
[![Package](https://img.shields.io/pypi/pyversions/k3portlock)](https://pypi.org/project/k3portlock)

Cross-process lock using TCP port binding.

k3portlock is a component of [pykit3](https://github.com/pykit3) project: a python3 toolkit set.

## Installation

```bash
pip install k3portlock
```

## Quick Start

```python
from k3portlock import Portlock, PortlockTimeout

# Using context manager (recommended)
with Portlock('my-resource', timeout=10):
    # Critical section - only one process can be here at a time
    print("Got the lock!")

# Manual acquire/release
lock = Portlock('another-resource')
try:
    lock.acquire()
    # Do work...
finally:
    lock.release()

# Handle timeout
try:
    with Portlock('busy-resource', timeout=5):
        pass
except PortlockTimeout:
    print("Could not acquire lock within 5 seconds")
```

## API Reference

::: k3portlock

## License

The MIT License (MIT) - Copyright (c) 2015 Zhang Yanpo (张炎泼)
