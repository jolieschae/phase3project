# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\io.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3616 bytes
__author__ = "Guido van Rossum <guido@python.org>, Mike Verdone <mike.verdone@gmail.com>, Mark Russell <mark.russell@zen.co.uk>, Antoine Pitrou <solipsis@pitrou.net>, Amaury Forgeot d'Arc <amauryfa@gmail.com>, Benjamin Peterson <benjamin@python.org>"
__all__ = [
 "'BlockingIOError'", "'open'", "'IOBase'", "'RawIOBase'", "'FileIO'", 
 "'BytesIO'", 
 "'StringIO'", "'BufferedIOBase'", 
 "'BufferedReader'", "'BufferedWriter'", 
 "'BufferedRWPair'", 
 "'BufferedRandom'", "'TextIOBase'", "'TextIOWrapper'", 
 "'UnsupportedOperation'", 
 "'SEEK_SET'", "'SEEK_CUR'", "'SEEK_END'"]
import _io, abc
from _io import DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation, open, FileIO, BytesIO, StringIO, BufferedReader, BufferedWriter, BufferedRWPair, BufferedRandom, IncrementalNewlineDecoder, TextIOWrapper
OpenWrapper = _io.open
UnsupportedOperation.__module__ = 'io'
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class IOBase(_io._IOBase, metaclass=abc.ABCMeta):
    __doc__ = _io._IOBase.__doc__


class RawIOBase(_io._RawIOBase, IOBase):
    __doc__ = _io._RawIOBase.__doc__


class BufferedIOBase(_io._BufferedIOBase, IOBase):
    __doc__ = _io._BufferedIOBase.__doc__


class TextIOBase(_io._TextIOBase, IOBase):
    __doc__ = _io._TextIOBase.__doc__


RawIOBase.register(FileIO)
for klass in (BytesIO, BufferedReader, BufferedWriter, BufferedRandom,
 BufferedRWPair):
    BufferedIOBase.register(klass)

for klass in (StringIO, TextIOWrapper):
    TextIOBase.register(klass)

del klass
try:
    from _io import _WindowsConsoleIO
except ImportError:
    pass
else:
    RawIOBase.register(_WindowsConsoleIO)