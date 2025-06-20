"""
Basic "operating system" services.

MicroPython module: https://docs.micropython.org/en/v1.24.0/library/os.html

CPython module: :mod:`python:os` https://docs.python.org/3/library/os.html .

The ``os`` module contains functions for filesystem access and mounting,
terminal redirection and duplication, and the ``uname`` and ``urandom``
functions.
"""

from __future__ import annotations
import sys
from _typeshed import (
    Incomplete,
    AnyStr_co,
    BytesPath,
    FileDescriptor,
    FileDescriptorLike,
    FileDescriptorOrPath,
    GenericPath,
    OpenBinaryMode,
    OpenBinaryModeReading,
    OpenBinaryModeUpdating,
    OpenBinaryModeWriting,
    OpenTextMode,
    ReadableBuffer,
    StrOrBytesPath,
    StrPath,
    SupportsLenAndGetItem,
    Unused,
    WriteableBuffer,
    structseq,
)
from abc import abstractmethod
from builtins import OSError
from collections.abc import Callable, Iterable, Iterator, Mapping, MutableMapping, Sequence
from contextlib import AbstractContextManager
from io import BufferedRandom, BufferedReader, BufferedWriter, FileIO, TextIOWrapper
from subprocess import Popen
from types import TracebackType
from typing import (
    Iterator,
    Optional,
    Tuple,
    IO,
    Any,
    AnyStr,
    BinaryIO,
    Final,
    Generic,
    Literal,
    NoReturn,
    Protocol,
    TypeVar,
    final,
    overload,
    runtime_checkable,
)
from typing_extensions import Awaitable, TypeVar, Self, TypeAlias, Unpack, deprecated

# from . import path as _path
from _mpy_shed import uname_result

if sys.version_info >= (3, 9):
    from types import GenericAlias

# This unnecessary alias is to work around various errors
# path = _path  # type: ignore

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")

# ----- os variables -----

# error = OSError

# supports_bytes_environ: bool

# supports_dir_fd: set[Callable[..., Any]]
# supports_fd: set[Callable[..., Any]]
# supports_effective_ids: set[Callable[..., Any]]
# supports_follow_symlinks: set[Callable[..., Any]]

if sys.platform != "win32":
    # Unix only
    PRIO_PROCESS: int
    PRIO_PGRP: int
    PRIO_USER: int

    F_LOCK: int
    F_TLOCK: int
    F_ULOCK: int
    F_TEST: int

    if sys.platform != "darwin":
        POSIX_FADV_NORMAL: int
        POSIX_FADV_SEQUENTIAL: int
        POSIX_FADV_RANDOM: int
        POSIX_FADV_NOREUSE: int
        POSIX_FADV_WILLNEED: int
        POSIX_FADV_DONTNEED: int

    if sys.platform != "linux" and sys.platform != "darwin":
        # In the os-module docs, these are marked as being available
        # on "Unix, not Emscripten, not WASI."
        # However, in the source code, a comment indicates they're "FreeBSD constants".
        # sys.platform could have one of many values on a FreeBSD Python build,
        # so the sys-module docs recommend doing `if sys.platform.startswith('freebsd')`
        # to detect FreeBSD builds. Unfortunately that would be too dynamic
        # for type checkers, however.
        SF_NODISKIO: int
        SF_MNOWAIT: int
        SF_SYNC: int

        if sys.version_info >= (3, 11):
            SF_NOCACHE: int

    if sys.platform == "linux":
        XATTR_SIZE_MAX: int
        XATTR_CREATE: int
        XATTR_REPLACE: int

    P_PID: int
    P_PGID: int
    P_ALL: int

    if sys.platform == "linux" and sys.version_info >= (3, 9):
        P_PIDFD: int

    WEXITED: int
    WSTOPPED: int
    WNOWAIT: int

    CLD_EXITED: int
    CLD_DUMPED: int
    CLD_TRAPPED: int
    CLD_CONTINUED: int

    if sys.version_info >= (3, 9):
        CLD_KILLED: int
        CLD_STOPPED: int

    # TODO: SCHED_RESET_ON_FORK not available on darwin?
    # TODO: SCHED_BATCH and SCHED_IDLE are linux only?
    SCHED_OTHER: int  # some flavors of Unix
    SCHED_BATCH: int  # some flavors of Unix
    SCHED_IDLE: int  # some flavors of Unix
    SCHED_SPORADIC: int  # some flavors of Unix
    SCHED_FIFO: int  # some flavors of Unix
    SCHED_RR: int  # some flavors of Unix
    SCHED_RESET_ON_FORK: int  # some flavors of Unix

if sys.platform != "win32":
    RTLD_LAZY: int
    RTLD_NOW: int
    RTLD_GLOBAL: int
    RTLD_LOCAL: int
    RTLD_NODELETE: int
    RTLD_NOLOAD: int

if sys.platform == "linux":
    RTLD_DEEPBIND: int
    GRND_NONBLOCK: int
    GRND_RANDOM: int

if sys.platform == "darwin" and sys.version_info >= (3, 12):
    PRIO_DARWIN_BG: int
    PRIO_DARWIN_NONUI: int
    PRIO_DARWIN_PROCESS: int
    PRIO_DARWIN_THREAD: int

# SEEK_SET: int
# SEEK_CUR: int
# SEEK_END: int
if sys.platform != "win32":
    SEEK_DATA: int  # some flavors of Unix
    SEEK_HOLE: int  # some flavors of Unix

# O_RDONLY: int
# O_WRONLY: int
# O_RDWR: int
# O_APPEND: int
# O_CREAT: int
# O_EXCL: int
# O_TRUNC: int
# We don't use sys.platform for O_* flags to denote platform-dependent APIs because some codes,
# including tests for mypy, use a more finer way than sys.platform before using these APIs
# See https://github.com/python/typeshed/pull/2286 for discussions
# O_DSYNC: int  # Unix only
# O_RSYNC: int  # Unix only
# O_SYNC: int  # Unix only
# O_NDELAY: int  # Unix only
# O_NONBLOCK: int  # Unix only
# O_NOCTTY: int  # Unix only
# O_CLOEXEC: int  # Unix only
# O_SHLOCK: int  # Unix only
# O_EXLOCK: int  # Unix only
# O_BINARY: int  # Windows only
# O_NOINHERIT: int  # Windows only
# O_SHORT_LIVED: int  # Windows only
# O_TEMPORARY: int  # Windows only
# O_RANDOM: int  # Windows only
# O_SEQUENTIAL: int  # Windows only
# O_TEXT: int  # Windows only
# O_ASYNC: int  # Gnu extension if in C library
# O_DIRECT: int  # Gnu extension if in C library
# O_DIRECTORY: int  # Gnu extension if in C library
# O_NOFOLLOW: int  # Gnu extension if in C library
# O_NOATIME: int  # Gnu extension if in C library
# O_PATH: int  # Gnu extension if in C library
# O_TMPFILE: int  # Gnu extension if in C library
# O_LARGEFILE: int  # Gnu extension if in C library
# O_ACCMODE: int  # TODO: when does this exist?

if sys.platform != "win32" and sys.platform != "darwin":
    # posix, but apparently missing on macos
    ST_APPEND: int
    ST_MANDLOCK: int
    ST_NOATIME: int
    ST_NODEV: int
    ST_NODIRATIME: int
    ST_NOEXEC: int
    ST_RELATIME: int
    ST_SYNCHRONOUS: int
    ST_WRITE: int

if sys.platform != "win32":
    NGROUPS_MAX: int
    ST_NOSUID: int
    ST_RDONLY: int

# curdir: str
# pardir: str
# sep: str
if sys.platform == "win32":
    altsep: str
else:
    altsep: str | None
# extsep: str
# pathsep: str
# defpath: str
# linesep: str
# devnull: str
# name: str

# F_OK: int
# R_OK: int
# W_OK: int
# X_OK: int

_EnvironCodeFunc: TypeAlias = Callable[[AnyStr], AnyStr]

class _Environ(MutableMapping[AnyStr, AnyStr], Generic[AnyStr]):
    encodekey: _EnvironCodeFunc[AnyStr]
    decodekey: _EnvironCodeFunc[AnyStr]
    encodevalue: _EnvironCodeFunc[AnyStr]
    decodevalue: _EnvironCodeFunc[AnyStr]
    if sys.version_info >= (3, 9):
        def __init__(
            self,
            data: MutableMapping[AnyStr, AnyStr],
            encodekey: _EnvironCodeFunc[AnyStr],
            decodekey: _EnvironCodeFunc[AnyStr],
            encodevalue: _EnvironCodeFunc[AnyStr],
            decodevalue: _EnvironCodeFunc[AnyStr],
        ) -> None: ...
    else:
        putenv: Callable[[AnyStr, AnyStr], object]
        unsetenv: Callable[[AnyStr, AnyStr], object]
        def __init__(
            self,
            data: MutableMapping[AnyStr, AnyStr],
            encodekey: _EnvironCodeFunc[AnyStr],
            decodekey: _EnvironCodeFunc[AnyStr],
            encodevalue: _EnvironCodeFunc[AnyStr],
            decodevalue: _EnvironCodeFunc[AnyStr],
            putenv: Callable[[AnyStr, AnyStr], object],
            unsetenv: Callable[[AnyStr, AnyStr], object],
        ) -> None: ...

    def setdefault(self, key: AnyStr, value: AnyStr) -> AnyStr: ...
    def copy(self) -> dict[AnyStr, AnyStr]: ...
    def __delitem__(self, key: AnyStr) -> None: ...
    def __getitem__(self, key: AnyStr) -> AnyStr: ...
    def __setitem__(self, key: AnyStr, value: AnyStr) -> None: ...
    def __iter__(self) -> Iterator[AnyStr]: ...
    def __len__(self) -> int: ...
    if sys.version_info >= (3, 9):
        def __or__(self, other: Mapping[_T1, _T2]) -> dict[AnyStr | _T1, AnyStr | _T2]: ...
        def __ror__(self, other: Mapping[_T1, _T2]) -> dict[AnyStr | _T1, AnyStr | _T2]: ...
        # We use @overload instead of a Union for reasons similar to those given for
        # overloading MutableMapping.update in stdlib/typing.pyi
        # The type: ignore is needed due to incompatible __or__/__ior__ signatures
        @overload  # type: ignore[misc]
        def __ior__(self, other: Mapping[AnyStr, AnyStr]) -> Self: ...
        @overload
        def __ior__(self, other: Iterable[tuple[AnyStr, AnyStr]]) -> Self: ...

# environ: _Environ[str]
if sys.platform != "win32":
    environb: _Environ[bytes]

if sys.version_info >= (3, 11) or sys.platform != "win32":
    EX_OK: int

if sys.platform != "win32":
    confstr_names: dict[str, int]
    pathconf_names: dict[str, int]
    sysconf_names: dict[str, int]

    EX_USAGE: int
    EX_DATAERR: int
    EX_NOINPUT: int
    EX_NOUSER: int
    EX_NOHOST: int
    EX_UNAVAILABLE: int
    EX_SOFTWARE: int
    EX_OSERR: int
    EX_OSFILE: int
    EX_CANTCREAT: int
    EX_IOERR: int
    EX_TEMPFAIL: int
    EX_PROTOCOL: int
    EX_NOPERM: int
    EX_CONFIG: int

# Exists on some Unix platforms, e.g. Solaris.
if sys.platform != "win32" and sys.platform != "darwin" and sys.platform != "linux":
    EX_NOTFOUND: int

# P_NOWAIT: int
# P_NOWAITO: int
# P_WAIT: int
if sys.platform == "win32":
    P_DETACH: int
    P_OVERLAY: int

# wait()/waitpid() options
if sys.platform != "win32":
    WNOHANG: int  # Unix only
    WCONTINUED: int  # some Unix systems
    WUNTRACED: int  # Unix only

# TMP_MAX: int  # Undocumented, but used by tempfile

# ----- os classes (structures) -----
@final
class stat_result(structseq[float], tuple[int, int, int, int, int, int, int, float, float, float]):
    # The constructor of this class takes an iterable of variable length (though it must be at least 10).
    #
    # However, this class behaves like a tuple of 10 elements,
    # no matter how long the iterable supplied to the constructor is.
    # https://github.com/python/typeshed/pull/6560#discussion_r767162532
    #
    # The 10 elements always present are st_mode, st_ino, st_dev, st_nlink,
    # st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime.
    #
    # More items may be added at the end by some implementations.
    if sys.version_info >= (3, 10):
        __match_args__: Final = ("st_mode", "st_ino", "st_dev", "st_nlink", "st_uid", "st_gid", "st_size")

    @property
    def st_mode(self) -> int: ...  # protection bits,
    @property
    def st_ino(self) -> int: ...  # inode number,
    @property
    def st_dev(self) -> int: ...  # device,
    @property
    def st_nlink(self) -> int: ...  # number of hard links,
    @property
    def st_uid(self) -> int: ...  # user id of owner,
    @property
    def st_gid(self) -> int: ...  # group id of owner,
    @property
    def st_size(self) -> int: ...  # size of file, in bytes,
    @property
    def st_atime(self) -> float: ...  # time of most recent access,
    @property
    def st_mtime(self) -> float: ...  # time of most recent content modification,
    # platform dependent (time of most recent metadata change on Unix, or the time of creation on Windows)
    if sys.version_info >= (3, 12) and sys.platform == "win32":
        @property
        @deprecated(
            """\
Use st_birthtime instead to retrieve the file creation time. \
In the future, this property will contain the last metadata change time."""
        )
        def st_ctime(self) -> float: ...
    else:
        @property
        def st_ctime(self) -> float: ...

    @property
    def st_atime_ns(self) -> int: ...  # time of most recent access, in nanoseconds
    @property
    def st_mtime_ns(self) -> int: ...  # time of most recent content modification in nanoseconds
    # platform dependent (time of most recent metadata change on Unix, or the time of creation on Windows) in nanoseconds
    @property
    def st_ctime_ns(self) -> int: ...
    if sys.platform == "win32":
        @property
        def st_file_attributes(self) -> int: ...
        @property
        def st_reparse_tag(self) -> int: ...
        if sys.version_info >= (3, 12):
            @property
            def st_birthtime(self) -> float: ...  # time of file creation in seconds
            @property
            def st_birthtime_ns(self) -> int: ...  # time of file creation in nanoseconds
    else:
        @property
        def st_blocks(self) -> int: ...  # number of blocks allocated for file
        @property
        def st_blksize(self) -> int: ...  # filesystem blocksize
        @property
        def st_rdev(self) -> int: ...  # type of device if an inode device
        if sys.platform != "linux":
            # These properties are available on MacOS, but not Ubuntu.
            # On other Unix systems (such as FreeBSD), the following attributes may be
            # available (but may be only filled out if root tries to use them):
            @property
            def st_gen(self) -> int: ...  # file generation number
            @property
            def st_birthtime(self) -> float: ...  # time of file creation in seconds
    if sys.platform == "darwin":
        @property
        def st_flags(self) -> int: ...  # user defined flags for file
    # Attributes documented as sometimes appearing, but deliberately omitted from the stub: `st_creator`, `st_rsize`, `st_type`.
    # See https://github.com/python/typeshed/pull/6560#issuecomment-991253327

@runtime_checkable
class PathLike(Protocol[AnyStr_co]):
    @abstractmethod
    def __fspath__(self) -> AnyStr_co: ...

@overload
def listdir(path: StrPath | None = None) -> list[str]: ...
@overload
def listdir(path: BytesPath) -> list[bytes]: ...
@overload
def listdir(path: int) -> list[str]: ...
@overload
def listdir(dir: Optional[Any] = None) -> Incomplete:
    """
    With no argument, list the current directory.  Otherwise list the given directory.
    """
    ...

@overload
def listdir(dir: Optional[Any] = None) -> Incomplete:
    """
    With no argument, list the current directory.  Otherwise list the given directory.
    """
    ...

@final
class DirEntry(Generic[AnyStr]):
    # This is what the scandir iterator yields
    # The constructor is hidden

    @property
    def name(self) -> AnyStr: ...
    @property
    def path(self) -> AnyStr: ...
    def inode(self) -> int: ...
    def is_dir(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_file(self, *, follow_symlinks: bool = True) -> bool: ...
    def is_symlink(self) -> bool: ...
    def stat(self, *, follow_symlinks: bool = True) -> stat_result: ...
    def __fspath__(self) -> AnyStr: ...
    if sys.version_info >= (3, 9):
        def __class_getitem__(cls, item: Any, /) -> GenericAlias: ...
    if sys.version_info >= (3, 12):
        def is_junction(self) -> bool: ...

@final
class statvfs_result(structseq[int], tuple[int, int, int, int, int, int, int, int, int, int, int]):
    if sys.version_info >= (3, 10):
        __match_args__: Final = (
            "f_bsize",
            "f_frsize",
            "f_blocks",
            "f_bfree",
            "f_bavail",
            "f_files",
            "f_ffree",
            "f_favail",
            "f_flag",
            "f_namemax",
        )

    @property
    def f_bsize(self) -> int: ...
    @property
    def f_frsize(self) -> int: ...
    @property
    def f_blocks(self) -> int: ...
    @property
    def f_bfree(self) -> int: ...
    @property
    def f_bavail(self) -> int: ...
    @property
    def f_files(self) -> int: ...
    @property
    def f_ffree(self) -> int: ...
    @property
    def f_favail(self) -> int: ...
    @property
    def f_flag(self) -> int: ...
    @property
    def f_namemax(self) -> int: ...
    @property
    def f_fsid(self) -> int: ...

# ----- os function stubs -----
def fsencode(filename: StrOrBytesPath) -> bytes: ...
def fsdecode(filename: StrOrBytesPath) -> str: ...
@overload
def fspath(path: str) -> str: ...
@overload
def fspath(path: bytes) -> bytes: ...
@overload
def fspath(path: PathLike[AnyStr]) -> AnyStr: ...
def get_exec_path(env: Mapping[str, str] | None = None) -> list[str]: ...
def getlogin() -> str: ...
def getpid() -> int: ...
def getppid() -> int: ...
def strerror(code: int, /) -> str: ...
def umask(mask: int, /) -> int: ...
@final
class uname_result(structseq[str], tuple[str, str, str, str, str]):
    if sys.version_info >= (3, 10):
        __match_args__: Final = ("sysname", "nodename", "release", "version", "machine")

    @property
    def sysname(self) -> str: ...
    @property
    def nodename(self) -> str: ...
    @property
    def release(self) -> str: ...
    @property
    def version(self) -> str: ...
    @property
    def machine(self) -> str: ...

if sys.platform != "win32":
    def ctermid() -> str: ...
    def getegid() -> int: ...
    def geteuid() -> int: ...
    def getgid() -> int: ...
    def getgrouplist(user: str, group: int, /) -> list[int]: ...
    def getgroups() -> list[int]: ...  # Unix only, behaves differently on Mac
    def initgroups(username: str, gid: int, /) -> None: ...
    def getpgid(pid: int) -> int: ...
    def getpgrp() -> int: ...
    def getpriority(which: int, who: int) -> int: ...
    def setpriority(which: int, who: int, priority: int) -> None: ...
    if sys.platform != "darwin":
        def getresuid() -> tuple[int, int, int]: ...
        def getresgid() -> tuple[int, int, int]: ...

    def getuid() -> int: ...
    def setegid(egid: int, /) -> None: ...
    def seteuid(euid: int, /) -> None: ...
    def setgid(gid: int, /) -> None: ...
    def setgroups(groups: Sequence[int], /) -> None: ...
    def setpgrp() -> None: ...
    def setpgid(pid: int, pgrp: int, /) -> None: ...
    def setregid(rgid: int, egid: int, /) -> None: ...
    if sys.platform != "darwin":
        def setresgid(rgid: int, egid: int, sgid: int, /) -> None: ...
        def setresuid(ruid: int, euid: int, suid: int, /) -> None: ...

    def setreuid(ruid: int, euid: int, /) -> None: ...
    def getsid(pid: int, /) -> int: ...
    def setsid() -> None: ...
    def setuid(uid: int, /) -> None: ...
    def uname() -> uname_result:
        """
        Return a tuple (possibly a named tuple) containing information about the
        underlying machine and/or its operating system.  The tuple has five fields
        in the following order, each of them being a string:

             * ``sysname`` -- the name of the underlying system
             * ``nodename`` -- the network name (can be the same as ``sysname``)
             * ``release`` -- the version of the underlying system
             * ``version`` -- the MicroPython version and build date
             * ``machine`` -- an identifier for the underlying hardware (eg board, CPU)
        """
        ...

@overload
def getenv(key: str) -> str | None: ...
@overload
def getenv(key: str, default: _T) -> str | _T: ...

if sys.platform != "win32":
    @overload
    def getenvb(key: bytes) -> bytes | None: ...
    @overload
    def getenvb(key: bytes, default: _T) -> bytes | _T: ...
    def putenv(name: StrOrBytesPath, value: StrOrBytesPath, /) -> None: ...
    def unsetenv(name: StrOrBytesPath, /) -> None: ...

else:
    def putenv(name: str, value: str, /) -> None: ...

    if sys.version_info >= (3, 9):
        def unsetenv(name: str, /) -> None: ...

_Opener: TypeAlias = Callable[[str, int], int]

@overload
def fdopen(
    fd: int,
    mode: OpenTextMode = "r",
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = ...,
    newline: str | None = ...,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> TextIOWrapper: ...
@overload
def fdopen(
    fd: int,
    mode: OpenBinaryMode,
    buffering: Literal[0],
    encoding: None = None,
    errors: None = None,
    newline: None = None,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> FileIO: ...
@overload
def fdopen(
    fd: int,
    mode: OpenBinaryModeUpdating,
    buffering: Literal[-1, 1] = -1,
    encoding: None = None,
    errors: None = None,
    newline: None = None,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> BufferedRandom: ...
@overload
def fdopen(
    fd: int,
    mode: OpenBinaryModeWriting,
    buffering: Literal[-1, 1] = -1,
    encoding: None = None,
    errors: None = None,
    newline: None = None,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> BufferedWriter: ...
@overload
def fdopen(
    fd: int,
    mode: OpenBinaryModeReading,
    buffering: Literal[-1, 1] = -1,
    encoding: None = None,
    errors: None = None,
    newline: None = None,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> BufferedReader: ...
@overload
def fdopen(
    fd: int,
    mode: OpenBinaryMode,
    buffering: int = -1,
    encoding: None = None,
    errors: None = None,
    newline: None = None,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> BinaryIO: ...
@overload
def fdopen(
    fd: int,
    mode: str,
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = ...,
    newline: str | None = ...,
    closefd: bool = ...,
    opener: _Opener | None = ...,
) -> IO[Any]: ...
def close(fd: int) -> None: ...
def closerange(fd_low: int, fd_high: int, /) -> None: ...
def device_encoding(fd: int) -> str | None: ...
def dup(fd: int, /) -> int: ...
def dup2(fd: int, fd2: int, inheritable: bool = True) -> int: ...
def fstat(fd: int) -> stat_result: ...
def ftruncate(fd: int, length: int, /) -> None: ...
def fsync(fd: FileDescriptorLike) -> None: ...
def isatty(fd: int, /) -> bool: ...

if sys.platform != "win32" and sys.version_info >= (3, 11):
    def login_tty(fd: int, /) -> None: ...

if sys.version_info >= (3, 11):
    def lseek(fd: int, position: int, whence: int, /) -> int: ...

else:
    def lseek(fd: int, position: int, how: int, /) -> int: ...

def open(path: StrOrBytesPath, flags: int, mode: int = 0o777, *, dir_fd: int | None = None) -> int: ...
def pipe() -> tuple[int, int]: ...
def read(fd: int, length: int, /) -> bytes: ...

if sys.version_info >= (3, 12) or sys.platform != "win32":
    def get_blocking(fd: int, /) -> bool: ...
    def set_blocking(fd: int, blocking: bool, /) -> None: ...

if sys.platform != "win32":
    def fchown(fd: int, uid: int, gid: int) -> None: ...
    def fpathconf(fd: int, name: str | int, /) -> int: ...
    def fstatvfs(fd: int, /) -> statvfs_result: ...
    def lockf(fd: int, command: int, length: int, /) -> None: ...
    def openpty() -> tuple[int, int]: ...  # some flavors of Unix
    if sys.platform != "darwin":
        def fdatasync(fd: FileDescriptorLike) -> None: ...
        def pipe2(flags: int, /) -> tuple[int, int]: ...  # some flavors of Unix
        def posix_fallocate(fd: int, offset: int, length: int, /) -> None: ...
        def posix_fadvise(fd: int, offset: int, length: int, advice: int, /) -> None: ...

    def pread(fd: int, length: int, offset: int, /) -> bytes: ...
    def pwrite(fd: int, buffer: ReadableBuffer, offset: int, /) -> int: ...
    # In CI, stubtest sometimes reports that these are available on MacOS, sometimes not
    def preadv(fd: int, buffers: SupportsLenAndGetItem[WriteableBuffer], offset: int, flags: int = 0, /) -> int: ...
    def pwritev(fd: int, buffers: SupportsLenAndGetItem[ReadableBuffer], offset: int, flags: int = 0, /) -> int: ...
    if sys.platform != "darwin":
        if sys.version_info >= (3, 10):
            RWF_APPEND: int  # docs say available on 3.7+, stubtest says otherwise
        RWF_DSYNC: int
        RWF_SYNC: int
        RWF_HIPRI: int
        RWF_NOWAIT: int

    if sys.platform == "linux":
        def sendfile(out_fd: FileDescriptor, in_fd: FileDescriptor, offset: int | None, count: int) -> int: ...
    else:
        def sendfile(
            out_fd: FileDescriptor,
            in_fd: FileDescriptor,
            offset: int,
            count: int,
            headers: Sequence[ReadableBuffer] = ...,
            trailers: Sequence[ReadableBuffer] = ...,
            flags: int = 0,
        ) -> int: ...  # FreeBSD and Mac OS X only

    def readv(fd: int, buffers: SupportsLenAndGetItem[WriteableBuffer], /) -> int: ...
    def writev(fd: int, buffers: SupportsLenAndGetItem[ReadableBuffer], /) -> int: ...

@final
class terminal_size(structseq[int], tuple[int, int]):
    if sys.version_info >= (3, 10):
        __match_args__: Final = ("columns", "lines")

    @property
    def columns(self) -> int: ...
    @property
    def lines(self) -> int: ...

def get_terminal_size(fd: int = ..., /) -> terminal_size: ...
def get_inheritable(fd: int, /) -> bool: ...
def set_inheritable(fd: int, inheritable: bool, /) -> None: ...

if sys.platform == "win32":
    def get_handle_inheritable(handle: int, /) -> bool: ...
    def set_handle_inheritable(handle: int, inheritable: bool, /) -> None: ...

if sys.platform != "win32":
    # Unix only
    def tcgetpgrp(fd: int, /) -> int: ...
    def tcsetpgrp(fd: int, pgid: int, /) -> None: ...
    def ttyname(fd: int, /) -> str: ...

def write(fd: int, data: ReadableBuffer, /) -> int: ...
def access(
    path: FileDescriptorOrPath, mode: int, *, dir_fd: int | None = None, effective_ids: bool = False, follow_symlinks: bool = True
) -> bool: ...
@overload
def chdir(path) -> Incomplete:
    """
    Change current directory.
    """
    ...

@overload
def chdir(path) -> Incomplete:
    """
    Change current directory.
    """
    ...

if sys.platform != "win32":
    def fchdir(fd: FileDescriptorLike) -> None: ...

@overload
def getcwd() -> Incomplete:
    """
    Get the current directory.
    """
    ...

@overload
def getcwd() -> Incomplete:
    """
    Get the current directory.
    """
    ...

def getcwdb() -> bytes: ...
def chmod(path: FileDescriptorOrPath, mode: int, *, dir_fd: int | None = None, follow_symlinks: bool = ...) -> None: ...

if sys.platform != "win32" and sys.platform != "linux":
    def chflags(path: StrOrBytesPath, flags: int, follow_symlinks: bool = True) -> None: ...  # some flavors of Unix
    def lchflags(path: StrOrBytesPath, flags: int) -> None: ...

if sys.platform != "win32":
    def chroot(path: StrOrBytesPath) -> None: ...
    def chown(path: FileDescriptorOrPath, uid: int, gid: int, *, dir_fd: int | None = None, follow_symlinks: bool = True) -> None: ...
    def lchown(path: StrOrBytesPath, uid: int, gid: int) -> None: ...

def link(
    src: StrOrBytesPath,
    dst: StrOrBytesPath,
    *,
    src_dir_fd: int | None = None,
    dst_dir_fd: int | None = None,
    follow_symlinks: bool = True,
) -> None: ...
def lstat(path: StrOrBytesPath, *, dir_fd: int | None = None) -> stat_result: ...
@overload
def mkdir(path) -> Incomplete:
    """
    Create a new directory.
    """
    ...

@overload
def mkdir(path) -> Incomplete:
    """
    Create a new directory.
    """
    ...

if sys.platform != "win32":
    def mkfifo(path: StrOrBytesPath, mode: int = 0o666, *, dir_fd: int | None = None) -> None: ...  # Unix only

def makedirs(name: StrOrBytesPath, mode: int = 0o777, exist_ok: bool = False) -> None: ...

if sys.platform != "win32":
    def mknod(path: StrOrBytesPath, mode: int = 0o600, device: int = 0, *, dir_fd: int | None = None) -> None: ...
    def major(device: int, /) -> int: ...
    def minor(device: int, /) -> int: ...
    def makedev(major: int, minor: int, /) -> int: ...
    def pathconf(path: FileDescriptorOrPath, name: str | int) -> int: ...  # Unix only

def readlink(path: GenericPath[AnyStr], *, dir_fd: int | None = None) -> AnyStr: ...
@overload
def remove(path) -> None:
    """
    Remove a file.
    """
    ...

@overload
def remove(path) -> None:
    """
    Remove a file.
    """
    ...

def removedirs(name: StrOrBytesPath) -> None: ...
@overload
def rename(old_path, new_path) -> None:
    """
    Rename a file.
    """
    ...

@overload
def rename(old_path, new_path) -> None:
    """
    Rename a file.
    """
    ...

def renames(old: StrOrBytesPath, new: StrOrBytesPath) -> None: ...
def replace(src: StrOrBytesPath, dst: StrOrBytesPath, *, src_dir_fd: int | None = None, dst_dir_fd: int | None = None) -> None: ...
@overload
def rmdir(path) -> None:
    """
    Remove a directory.
    """
    ...

@overload
def rmdir(path) -> None:
    """
    Remove a directory.
    """
    ...

class _ScandirIterator(Iterator[DirEntry[AnyStr]], AbstractContextManager[_ScandirIterator[AnyStr], None]):
    def __next__(self) -> DirEntry[AnyStr]: ...
    def __exit__(self, *args: Unused) -> None: ...
    def close(self) -> None: ...

@overload
def scandir(path: None = None) -> _ScandirIterator[str]: ...
@overload
def scandir(path: int) -> _ScandirIterator[str]: ...
@overload
def scandir(path: GenericPath[AnyStr]) -> _ScandirIterator[AnyStr]: ...
def stat(path: str | bytes) -> stat_result:
    """
    Get the status of a file or directory.
    """
    ...

if sys.platform != "win32":

    @overload
    def statvfs(path) -> Tuple:
        """
        Get the status of a filesystem.

        Returns a tuple with the filesystem information in the following order:

             * ``f_bsize`` -- file system block size
             * ``f_frsize`` -- fragment size
             * ``f_blocks`` -- size of fs in f_frsize units
             * ``f_bfree`` -- number of free blocks
             * ``f_bavail`` -- number of free blocks for unprivileged users
             * ``f_files`` -- number of inodes
             * ``f_ffree`` -- number of free inodes
             * ``f_favail`` -- number of free inodes for unprivileged users
             * ``f_flag`` -- mount flags
             * ``f_namemax`` -- maximum filename length

        Parameters related to inodes: ``f_files``, ``f_ffree``, ``f_avail``
        and the ``f_flags`` parameter may return ``0`` as they can be unavailable
        in a port-specific implementation.
        """
        ...

def symlink(src: StrOrBytesPath, dst: StrOrBytesPath, target_is_directory: bool = False, *, dir_fd: int | None = None) -> None: ...

if sys.platform != "win32":

    @overload
    def sync() -> None:
        """
        Sync all filesystems.
        """
        ...

def truncate(path: FileDescriptorOrPath, length: int) -> None: ...  # Unix only up to version 3.4
def unlink(path: StrOrBytesPath, *, dir_fd: int | None = None) -> None: ...
def utime(
    path: FileDescriptorOrPath,
    times: tuple[int, int] | tuple[float, float] | None = None,
    *,
    ns: tuple[int, int] = ...,
    dir_fd: int | None = None,
    follow_symlinks: bool = True,
) -> None: ...

_OnError: TypeAlias = Callable[[OSError], object]

def walk(
    top: GenericPath[AnyStr], topdown: bool = True, onerror: _OnError | None = None, followlinks: bool = False
) -> Iterator[tuple[AnyStr, list[AnyStr], list[AnyStr]]]: ...

if sys.platform != "win32":
    @overload
    def fwalk(
        top: StrPath = ".",
        topdown: bool = True,
        onerror: _OnError | None = None,
        *,
        follow_symlinks: bool = False,
        dir_fd: int | None = None,
    ) -> Iterator[tuple[str, list[str], list[str], int]]: ...
    @overload
    def fwalk(
        top: BytesPath,
        topdown: bool = True,
        onerror: _OnError | None = None,
        *,
        follow_symlinks: bool = False,
        dir_fd: int | None = None,
    ) -> Iterator[tuple[bytes, list[bytes], list[bytes], int]]: ...
    if sys.platform == "linux":
        def getxattr(path: FileDescriptorOrPath, attribute: StrOrBytesPath, *, follow_symlinks: bool = True) -> bytes: ...
        def listxattr(path: FileDescriptorOrPath | None = None, *, follow_symlinks: bool = True) -> list[str]: ...
        def removexattr(path: FileDescriptorOrPath, attribute: StrOrBytesPath, *, follow_symlinks: bool = True) -> None: ...
        def setxattr(
            path: FileDescriptorOrPath,
            attribute: StrOrBytesPath,
            value: ReadableBuffer,
            flags: int = 0,
            *,
            follow_symlinks: bool = True,
        ) -> None: ...

def abort() -> NoReturn: ...

# These are defined as execl(file, *args) but the first *arg is mandatory.
def execl(file: StrOrBytesPath, *args: Unpack[tuple[StrOrBytesPath, Unpack[tuple[StrOrBytesPath, ...]]]]) -> NoReturn: ...
def execlp(file: StrOrBytesPath, *args: Unpack[tuple[StrOrBytesPath, Unpack[tuple[StrOrBytesPath, ...]]]]) -> NoReturn: ...

# These are: execle(file, *args, env) but env is pulled from the last element of the args.
def execle(file: StrOrBytesPath, *args: Unpack[tuple[StrOrBytesPath, Unpack[tuple[StrOrBytesPath, ...]], _ExecEnv]]) -> NoReturn: ...
def execlpe(file: StrOrBytesPath, *args: Unpack[tuple[StrOrBytesPath, Unpack[tuple[StrOrBytesPath, ...]], _ExecEnv]]) -> NoReturn: ...

# The docs say `args: tuple or list of strings`
# The implementation enforces tuple or list so we can't use Sequence.
# Not separating out PathLike[str] and PathLike[bytes] here because it doesn't make much difference
# in practice, and doing so would explode the number of combinations in this already long union.
# All these combinations are necessary due to list being invariant.
_ExecVArgs: TypeAlias = (
    tuple[StrOrBytesPath, ...]
    | list[bytes]
    | list[str]
    | list[PathLike[Any]]
    | list[bytes | str]
    | list[bytes | PathLike[Any]]
    | list[str | PathLike[Any]]
    | list[bytes | str | PathLike[Any]]
)
# Depending on the OS, the keys and values are passed either to
# PyUnicode_FSDecoder (which accepts str | ReadableBuffer) or to
# PyUnicode_FSConverter (which accepts StrOrBytesPath). For simplicity,
# we limit to str | bytes.
_ExecEnv: TypeAlias = Mapping[bytes, bytes | str] | Mapping[str, bytes | str]

def execv(path: StrOrBytesPath, argv: _ExecVArgs, /) -> NoReturn: ...
def execve(path: FileDescriptorOrPath, argv: _ExecVArgs, env: _ExecEnv) -> NoReturn: ...
def execvp(file: StrOrBytesPath, args: _ExecVArgs) -> NoReturn: ...
def execvpe(file: StrOrBytesPath, args: _ExecVArgs, env: _ExecEnv) -> NoReturn: ...
def _exit(status: int) -> NoReturn: ...
def kill(pid: int, signal: int, /) -> None: ...

if sys.platform != "win32":
    # Unix only
    def fork() -> int: ...
    def forkpty() -> tuple[int, int]: ...  # some flavors of Unix
    def killpg(pgid: int, signal: int, /) -> None: ...
    def nice(increment: int, /) -> int: ...
    if sys.platform != "darwin" and sys.platform != "linux":
        def plock(op: int, /) -> None: ...

class _wrap_close:
    def __init__(self, stream: TextIOWrapper, proc: Popen[str]) -> None: ...
    def close(self) -> int | None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    # Methods below here don't exist directly on the _wrap_close object, but
    # are copied from the wrapped TextIOWrapper object via __getattr__.
    # The full set of TextIOWrapper methods are technically available this way,
    # but undocumented. Only a subset are currently included here.
    def read(self, size: int | None = -1, /) -> str: ...
    def readable(self) -> bool: ...
    def readline(self, size: int = -1, /) -> str: ...
    def readlines(self, hint: int = -1, /) -> list[str]: ...
    def writable(self) -> bool: ...
    def write(self, s: str, /) -> int: ...
    def writelines(self, lines: Iterable[str], /) -> None: ...

def popen(cmd: str, mode: str = "r", buffering: int = -1) -> _wrap_close: ...
def spawnl(mode: int, file: StrOrBytesPath, arg0: StrOrBytesPath, *args: StrOrBytesPath) -> int: ...
def spawnle(mode: int, file: StrOrBytesPath, arg0: StrOrBytesPath, *args: Any) -> int: ...  # Imprecise sig

if sys.platform != "win32":
    def spawnv(mode: int, file: StrOrBytesPath, args: _ExecVArgs) -> int: ...
    def spawnve(mode: int, file: StrOrBytesPath, args: _ExecVArgs, env: _ExecEnv) -> int: ...

else:
    def spawnv(mode: int, path: StrOrBytesPath, argv: _ExecVArgs, /) -> int: ...
    def spawnve(mode: int, path: StrOrBytesPath, argv: _ExecVArgs, env: _ExecEnv, /) -> int: ...

def system(command: StrOrBytesPath) -> int: ...
@final
class times_result(structseq[float], tuple[float, float, float, float, float]):
    if sys.version_info >= (3, 10):
        __match_args__: Final = ("user", "system", "children_user", "children_system", "elapsed")

    @property
    def user(self) -> float: ...
    @property
    def system(self) -> float: ...
    @property
    def children_user(self) -> float: ...
    @property
    def children_system(self) -> float: ...
    @property
    def elapsed(self) -> float: ...

def times() -> times_result: ...
def waitpid(pid: int, options: int, /) -> tuple[int, int]: ...

if sys.platform == "win32":
    if sys.version_info >= (3, 10):
        def startfile(
            filepath: StrOrBytesPath,
            operation: str = ...,
            arguments: str = "",
            cwd: StrOrBytesPath | None = None,
            show_cmd: int = 1,
        ) -> None: ...
    else:
        def startfile(filepath: StrOrBytesPath, operation: str = ...) -> None: ...

else:
    def spawnlp(mode: int, file: StrOrBytesPath, arg0: StrOrBytesPath, *args: StrOrBytesPath) -> int: ...
    def spawnlpe(mode: int, file: StrOrBytesPath, arg0: StrOrBytesPath, *args: Any) -> int: ...  # Imprecise signature
    def spawnvp(mode: int, file: StrOrBytesPath, args: _ExecVArgs) -> int: ...
    def spawnvpe(mode: int, file: StrOrBytesPath, args: _ExecVArgs, env: _ExecEnv) -> int: ...
    def wait() -> tuple[int, int]: ...  # Unix only
    # Added to MacOS in 3.13
    if sys.platform != "darwin" or sys.version_info >= (3, 13):
        @final
        class waitid_result(structseq[int], tuple[int, int, int, int, int]):
            if sys.version_info >= (3, 10):
                __match_args__: Final = ("si_pid", "si_uid", "si_signo", "si_status", "si_code")

            @property
            def si_pid(self) -> int: ...
            @property
            def si_uid(self) -> int: ...
            @property
            def si_signo(self) -> int: ...
            @property
            def si_status(self) -> int: ...
            @property
            def si_code(self) -> int: ...

        def waitid(idtype: int, ident: int, options: int, /) -> waitid_result | None: ...

    from resource import struct_rusage

    def wait3(options: int) -> tuple[int, int, struct_rusage]: ...
    def wait4(pid: int, options: int) -> tuple[int, int, struct_rusage]: ...
    def WCOREDUMP(status: int, /) -> bool: ...
    def WIFCONTINUED(status: int) -> bool: ...
    def WIFSTOPPED(status: int) -> bool: ...
    def WIFSIGNALED(status: int) -> bool: ...
    def WIFEXITED(status: int) -> bool: ...
    def WEXITSTATUS(status: int) -> int: ...
    def WSTOPSIG(status: int) -> int: ...
    def WTERMSIG(status: int) -> int: ...
    def posix_spawn(
        path: StrOrBytesPath,
        argv: _ExecVArgs,
        env: _ExecEnv,
        /,
        *,
        file_actions: Sequence[tuple[Any, ...]] | None = ...,
        setpgroup: int | None = ...,
        resetids: bool = ...,
        setsid: bool = ...,
        setsigmask: Iterable[int] = ...,
        setsigdef: Iterable[int] = ...,
        scheduler: tuple[Any, sched_param] | None = ...,
    ) -> int: ...
    def posix_spawnp(
        path: StrOrBytesPath,
        argv: _ExecVArgs,
        env: _ExecEnv,
        /,
        *,
        file_actions: Sequence[tuple[Any, ...]] | None = ...,
        setpgroup: int | None = ...,
        resetids: bool = ...,
        setsid: bool = ...,
        setsigmask: Iterable[int] = ...,
        setsigdef: Iterable[int] = ...,
        scheduler: tuple[Any, sched_param] | None = ...,
    ) -> int: ...
    POSIX_SPAWN_OPEN: int
    POSIX_SPAWN_CLOSE: int
    POSIX_SPAWN_DUP2: int

if sys.platform != "win32":
    @final
    class sched_param(structseq[int], tuple[int]):
        if sys.version_info >= (3, 10):
            __match_args__: Final = ("sched_priority",)

        def __new__(cls, sched_priority: int) -> Self: ...
        @property
        def sched_priority(self) -> int: ...

    def sched_get_priority_min(policy: int) -> int: ...  # some flavors of Unix
    def sched_get_priority_max(policy: int) -> int: ...  # some flavors of Unix
    def sched_yield() -> None: ...  # some flavors of Unix
    if sys.platform != "darwin":
        def sched_setscheduler(pid: int, policy: int, param: sched_param, /) -> None: ...  # some flavors of Unix
        def sched_getscheduler(pid: int, /) -> int: ...  # some flavors of Unix
        def sched_rr_get_interval(pid: int, /) -> float: ...  # some flavors of Unix
        def sched_setparam(pid: int, param: sched_param, /) -> None: ...  # some flavors of Unix
        def sched_getparam(pid: int, /) -> sched_param: ...  # some flavors of Unix
        def sched_setaffinity(pid: int, mask: Iterable[int], /) -> None: ...  # some flavors of Unix
        def sched_getaffinity(pid: int, /) -> set[int]: ...  # some flavors of Unix

def cpu_count() -> int | None: ...

if sys.version_info >= (3, 13):
    # Documented to return `int | None`, but falls back to `len(sched_getaffinity(0))` when
    # available. See https://github.com/python/cpython/blob/417c130/Lib/os.py#L1175-L1186.
    if sys.platform != "win32" and sys.platform != "darwin":
        def process_cpu_count() -> int: ...
    else:
        def process_cpu_count() -> int | None: ...

if sys.platform != "win32":
    # Unix only
    def confstr(name: str | int, /) -> str | None: ...
    def getloadavg() -> tuple[float, float, float]: ...
    def sysconf(name: str | int, /) -> int: ...

if sys.platform == "linux":
    def getrandom(size: int, flags: int = 0) -> bytes: ...

@overload
def urandom(n: int) -> bytes:
    """
    Return a bytes object with *n* random bytes. Whenever possible, it is
    generated by the hardware random number generator.
    """
    ...

@overload
def urandom(n: int) -> bytes:
    """
    Return a bytes object with *n* random bytes. Whenever possible, it is
    generated by the hardware random number generator.
    """
    ...

if sys.platform != "win32":
    def register_at_fork(
        *,
        before: Callable[..., Any] | None = ...,
        after_in_parent: Callable[..., Any] | None = ...,
        after_in_child: Callable[..., Any] | None = ...,
    ) -> None: ...

if sys.platform == "win32":
    class _AddedDllDirectory:
        path: str | None
        def __init__(self, path: str | None, cookie: _T, remove_dll_directory: Callable[[_T], object]) -> None: ...
        def close(self) -> None: ...
        def __enter__(self) -> Self: ...
        def __exit__(self, *args: Unused) -> None: ...

    def add_dll_directory(path: str) -> _AddedDllDirectory: ...

if sys.platform == "linux":
    MFD_CLOEXEC: int
    MFD_ALLOW_SEALING: int
    MFD_HUGETLB: int
    MFD_HUGE_SHIFT: int
    MFD_HUGE_MASK: int
    MFD_HUGE_64KB: int
    MFD_HUGE_512KB: int
    MFD_HUGE_1MB: int
    MFD_HUGE_2MB: int
    MFD_HUGE_8MB: int
    MFD_HUGE_16MB: int
    MFD_HUGE_32MB: int
    MFD_HUGE_256MB: int
    MFD_HUGE_512MB: int
    MFD_HUGE_1GB: int
    MFD_HUGE_2GB: int
    MFD_HUGE_16GB: int
    def memfd_create(name: str, flags: int = ...) -> int: ...
    def copy_file_range(src: int, dst: int, count: int, offset_src: int | None = ..., offset_dst: int | None = ...) -> int: ...

if sys.version_info >= (3, 9):
    def waitstatus_to_exitcode(status: int) -> int: ...

    if sys.platform == "linux":
        def pidfd_open(pid: int, flags: int = ...) -> int: ...

if sys.version_info >= (3, 12) and sys.platform == "win32":
    def listdrives() -> list[str]: ...
    def listmounts(volume: str) -> list[str]: ...
    def listvolumes() -> list[str]: ...

if sys.version_info >= (3, 10) and sys.platform == "linux":
    EFD_CLOEXEC: int
    EFD_NONBLOCK: int
    EFD_SEMAPHORE: int
    SPLICE_F_MORE: int
    SPLICE_F_MOVE: int
    SPLICE_F_NONBLOCK: int
    def eventfd(initval: int, flags: int = 524288) -> FileDescriptor: ...
    def eventfd_read(fd: FileDescriptor) -> int: ...
    def eventfd_write(fd: FileDescriptor, value: int) -> None: ...
    def splice(
        src: FileDescriptor,
        dst: FileDescriptor,
        count: int,
        offset_src: int | None = ...,
        offset_dst: int | None = ...,
        flags: int = 0,
    ) -> int: ...

if sys.version_info >= (3, 12) and sys.platform == "linux":
    CLONE_FILES: int
    CLONE_FS: int
    CLONE_NEWCGROUP: int  # Linux 4.6+
    CLONE_NEWIPC: int  # Linux 2.6.19+
    CLONE_NEWNET: int  # Linux 2.6.24+
    CLONE_NEWNS: int
    CLONE_NEWPID: int  # Linux 3.8+
    CLONE_NEWTIME: int  # Linux 5.6+
    CLONE_NEWUSER: int  # Linux 3.8+
    CLONE_NEWUTS: int  # Linux 2.6.19+
    CLONE_SIGHAND: int
    CLONE_SYSVSEM: int  # Linux 2.6.26+
    CLONE_THREAD: int
    CLONE_VM: int
    def unshare(flags: int) -> None: ...
    def setns(fd: FileDescriptorLike, nstype: int = 0) -> None: ...

if sys.version_info >= (3, 13) and sys.platform != "win32":
    def posix_openpt(oflag: int, /) -> int: ...
    def grantpt(fd: FileDescriptorLike, /) -> None: ...
    def unlockpt(fd: FileDescriptorLike, /) -> None: ...
    def ptsname(fd: FileDescriptorLike, /) -> str: ...

if sys.version_info >= (3, 13) and sys.platform == "linux":
    TFD_TIMER_ABSTIME: Final = 1
    TFD_TIMER_CANCEL_ON_SET: Final = 2
    TFD_NONBLOCK: Final[int]
    TFD_CLOEXEC: Final[int]
    POSIX_SPAWN_CLOSEFROM: Final[int]

    def timerfd_create(clockid: int, /, *, flags: int = 0) -> int: ...
    def timerfd_settime(fd: FileDescriptor, /, *, flags: int = 0, initial: float = 0.0, interval: float = 0.0) -> tuple[float, float]: ...
    def timerfd_settime_ns(fd: FileDescriptor, /, *, flags: int = 0, initial: int = 0, interval: int = 0) -> tuple[int, int]: ...
    def timerfd_gettime(fd: FileDescriptor, /) -> tuple[float, float]: ...
    def timerfd_gettime_ns(fd: FileDescriptor, /) -> tuple[int, int]: ...

if sys.version_info >= (3, 13) or sys.platform != "win32":
    # Added to Windows in 3.13.
    def fchmod(fd: int, mode: int) -> None: ...

if sys.platform != "linux":
    if sys.version_info >= (3, 13) or sys.platform != "win32":
        # Added to Windows in 3.13.
        def lchmod(path: StrOrBytesPath, mode: int) -> None: ...

@overload
def ilistdir(dir: Optional[Any] = None) -> Iterator[Tuple]:
    """
    This function returns an iterator which then yields tuples corresponding to
    the entries in the directory that it is listing.  With no argument it lists the
    current directory, otherwise it lists the directory given by *dir*.

    The tuples have the form *(name, type, inode[, size])*:

     - *name* is a string (or bytes if *dir* is a bytes object) and is the name of
       the entry;
     - *type* is an integer that specifies the type of the entry, with 0x4000 for
       directories and 0x8000 for regular files;
     - *inode* is an integer corresponding to the inode of the file, and may be 0
       for filesystems that don't have such a notion.
     - Some platforms may return a 4-tuple that includes the entry's *size*.  For
       file entries, *size* is an integer representing the size of the file
       or -1 if unknown.  Its meaning is currently undefined for directory
       entries.
    """
    ...

@overload
def ilistdir(dir: Optional[Any] = None) -> Iterator[Tuple]:
    """
    This function returns an iterator which then yields tuples corresponding to
    the entries in the directory that it is listing.  With no argument it lists the
    current directory, otherwise it lists the directory given by *dir*.

    The tuples have the form *(name, type, inode[, size])*:

     - *name* is a string (or bytes if *dir* is a bytes object) and is the name of
       the entry;
     - *type* is an integer that specifies the type of the entry, with 0x4000 for
       directories and 0x8000 for regular files;
     - *inode* is an integer corresponding to the inode of the file, and may be 0
       for filesystems that don't have such a notion.
     - Some platforms may return a 4-tuple that includes the entry's *size*.  For
       file entries, *size* is an integer representing the size of the file
       or -1 if unknown.  Its meaning is currently undefined for directory
       entries.
    """
    ...

@overload
def statvfs(path) -> Tuple:
    """
    Get the status of a filesystem.

    Returns a tuple with the filesystem information in the following order:

         * ``f_bsize`` -- file system block size
         * ``f_frsize`` -- fragment size
         * ``f_blocks`` -- size of fs in f_frsize units
         * ``f_bfree`` -- number of free blocks
         * ``f_bavail`` -- number of free blocks for unprivileged users
         * ``f_files`` -- number of inodes
         * ``f_ffree`` -- number of free inodes
         * ``f_favail`` -- number of free inodes for unprivileged users
         * ``f_flag`` -- mount flags
         * ``f_namemax`` -- maximum filename length

    Parameters related to inodes: ``f_files``, ``f_ffree``, ``f_avail``
    and the ``f_flags`` parameter may return ``0`` as they can be unavailable
    in a port-specific implementation.
    """
    ...

@overload
def sync() -> None:
    """
    Sync all filesystems.
    """
    ...

@overload
def dupterm(stream_object, index=0, /) -> IO:
    """
    Duplicate or switch the MicroPython terminal (the REPL) on the given `stream`-like
    object. The *stream_object* argument must be a native stream object, or derive
    from ``io.IOBase`` and implement the ``readinto()`` and
    ``write()`` methods.  The stream should be in non-blocking mode and
    ``readinto()`` should return ``None`` if there is no data available for reading.

    After calling this function all terminal output is repeated on this stream,
    and any input that is available on the stream is passed on to the terminal input.

    The *index* parameter should be a non-negative integer and specifies which
    duplication slot is set.  A given port may implement more than one slot (slot 0
    will always be available) and in that case terminal input and output is
    duplicated on all the slots that are set.

    If ``None`` is passed as the *stream_object* then duplication is cancelled on
    the slot given by *index*.

    The function returns the previous stream-like object in the given slot.
    """
    ...

@overload
def dupterm(stream_object, index=0, /) -> IO:
    """
    Duplicate or switch the MicroPython terminal (the REPL) on the given `stream`-like
    object. The *stream_object* argument must be a native stream object, or derive
    from ``io.IOBase`` and implement the ``readinto()`` and
    ``write()`` methods.  The stream should be in non-blocking mode and
    ``readinto()`` should return ``None`` if there is no data available for reading.

    After calling this function all terminal output is repeated on this stream,
    and any input that is available on the stream is passed on to the terminal input.

    The *index* parameter should be a non-negative integer and specifies which
    duplication slot is set.  A given port may implement more than one slot (slot 0
    will always be available) and in that case terminal input and output is
    duplicated on all the slots that are set.

    If ``None`` is passed as the *stream_object* then duplication is cancelled on
    the slot given by *index*.

    The function returns the previous stream-like object in the given slot.
    """
    ...

@overload
def mount(fsobj, mount_point, *, readonly=False) -> Incomplete:
    """
    See `vfs.mount`.
    """
    ...

@overload
def mount(fsobj, mount_point, *, readonly=False) -> Incomplete:
    """
    See `vfs.mount`.
    """
    ...

@overload
def umount(mount_point) -> Incomplete:
    """
    See `vfs.umount`.
    """
    ...

@overload
def umount(mount_point) -> Incomplete:
    """
    See `vfs.umount`.
    """
    ...

@overload  # force merge
def dupterm_notify(obj_in: Any, /) -> None:
    # https://github.com/orgs/micropython/discussions/16680
    """
    Notify the REPL that input is available on the stream-like object that was
    previously set by `dupterm`.  This is used by the stream-like object to
    notify the REPL that there is input available for reading.

    The *obj_in* argument must be the stream-like object that was previously set
    by `dupterm` or None .
    """
    ...
