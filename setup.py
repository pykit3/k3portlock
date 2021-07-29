# DO NOT EDIT!!! built with `python _building/build_setup.py`
import setuptools
setuptools.setup(
    name="k3portlock",
    packages=["k3portlock"],
    version="0.1.2",
    license='MIT',
    description='k3protlock is a cross-process lock that is implemented with `tcp` port binding.',
    long_description='# k3portlock\n\n[![Action-CI](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml/badge.svg)](https://github.com/pykit3/k3portlock/actions/workflows/python-package.yml)\n[![Build Status](https://travis-ci.com/pykit3/k3portlock.svg?branch=master)](https://travis-ci.com/pykit3/k3portlock)\n[![Documentation Status](https://readthedocs.org/projects/k3portlock/badge/?version=stable)](https://k3portlock.readthedocs.io/en/stable/?badge=stable)\n[![Package](https://img.shields.io/pypi/pyversions/k3portlock)](https://pypi.org/project/k3portlock)\n\nk3portlock is a cross-process lock that is implemented with `tcp` port binding.\n\nk3portlock is a component of [pykit3] project: a python3 toolkit set.\n\n\nk3portlock is a cross-process lock that is implemented with `tcp` port binding.\nSince no two processes could bind on a same TCP port.\n\nk3portlock tries to bind **3** ports on loopback ip `127.0.0.1`.\nIf a k3portlock instance succeeds on binding **2** ports out of 3,\nit is considered this instance has acquired the lock.\n\n\n\n\n# Install\n\n```\npip install k3portlock\n```\n\n#   Author\n\nZhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n#   Copyright and License\n\nThe MIT License (MIT)\n\nCopyright (c) 2015 Zhang Yanpo (张炎泼) <drdr.xp@gmail.com>\n\n\n[pykit3]: https://github.com/pykit3',
    long_description_content_type="text/markdown",
    author='Zhang Yanpo',
    author_email='drdr.xp@gmail.com',
    url='https://github.com/pykit3/k3portlock',
    keywords=['python', 'port', 'lock'],
    python_requires='>=3.0',

    install_requires=['k3ut<0.2,>=0.1.15'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
    ] + ['Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7', 'Programming Language :: Python :: 3.8', 'Programming Language :: Python :: Implementation :: PyPy'],
)
