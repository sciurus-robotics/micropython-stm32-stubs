"""
System error codes.

MicroPython module: https://docs.micropython.org/en/v1.25.0/library/errno.html

CPython module: :mod:`python:errno` https://docs.python.org/3/library/errno.html .

This module provides access to symbolic error codes for `OSError` exception.
A particular inventory of codes depends on :term:`MicroPython port`.

---
Module: 'errno' on micropython-v1.25.0-stm32-PYBV11
"""

# MCU: {'version': '1.25.0', 'mpy': 'v6.3', 'port': 'stm32', 'board': 'PYBV11', 'family': 'micropython', 'build': '', 'arch': 'armv7emsp', 'ver': '1.25.0', 'cpu': 'STM32F405RG'}
# Stubber: v1.24.0
from __future__ import annotations
from typing import Dict, Final
from _typeshed import Incomplete
from typing_extensions import Awaitable, TypeAlias, TypeVar

ENOBUFS: Final[int] = 105
ENODEV: Final[int] = 19
ENOENT: Final[int] = 2
EISDIR: Final[int] = 21
EIO: Final[int] = 5
EINVAL: Final[int] = 22
EPERM: Final[int] = 1
ETIMEDOUT: Final[int] = 110
ENOMEM: Final[int] = 12
EOPNOTSUPP: Final[int] = 95
ENOTCONN: Final[int] = 107
errorcode: dict = {}
EAGAIN: Final[int] = 11
EALREADY: Final[int] = 114
EBADF: Final[int] = 9
EADDRINUSE: Final[int] = 98
EACCES: Final[int] = 13
EINPROGRESS: Final[int] = 115
EEXIST: Final[int] = 17
EHOSTUNREACH: Final[int] = 113
ECONNABORTED: Final[int] = 103
ECONNRESET: Final[int] = 104
ECONNREFUSED: Final[int] = 111
ENOTSUP: Final[int] = ...
