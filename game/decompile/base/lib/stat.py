# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\stat.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 5216 bytes
ST_MODE = 0
ST_INO = 1
ST_DEV = 2
ST_NLINK = 3
ST_UID = 4
ST_GID = 5
ST_SIZE = 6
ST_ATIME = 7
ST_MTIME = 8
ST_CTIME = 9

def S_IMODE(mode):
    return mode & 4095


def S_IFMT(mode):
    return mode & 61440


S_IFDIR = 16384
S_IFCHR = 8192
S_IFBLK = 24576
S_IFREG = 32768
S_IFIFO = 4096
S_IFLNK = 40960
S_IFSOCK = 49152

def S_ISDIR(mode):
    return S_IFMT(mode) == S_IFDIR


def S_ISCHR(mode):
    return S_IFMT(mode) == S_IFCHR


def S_ISBLK(mode):
    return S_IFMT(mode) == S_IFBLK


def S_ISREG(mode):
    return S_IFMT(mode) == S_IFREG


def S_ISFIFO(mode):
    return S_IFMT(mode) == S_IFIFO


def S_ISLNK(mode):
    return S_IFMT(mode) == S_IFLNK


def S_ISSOCK(mode):
    return S_IFMT(mode) == S_IFSOCK


S_ISUID = 2048
S_ISGID = 1024
S_ENFMT = S_ISGID
S_ISVTX = 512
S_IREAD = 256
S_IWRITE = 128
S_IEXEC = 64
S_IRWXU = 448
S_IRUSR = 256
S_IWUSR = 128
S_IXUSR = 64
S_IRWXG = 56
S_IRGRP = 32
S_IWGRP = 16
S_IXGRP = 8
S_IRWXO = 7
S_IROTH = 4
S_IWOTH = 2
S_IXOTH = 1
UF_NODUMP = 1
UF_IMMUTABLE = 2
UF_APPEND = 4
UF_OPAQUE = 8
UF_NOUNLINK = 16
UF_COMPRESSED = 32
UF_HIDDEN = 32768
SF_ARCHIVED = 65536
SF_IMMUTABLE = 131072
SF_APPEND = 262144
SF_NOUNLINK = 1048576
SF_SNAPSHOT = 2097152
_filemode_table = (
 (
  (
   S_IFLNK, 'l'),
  (
   S_IFREG, '-'),
  (
   S_IFBLK, 'b'),
  (
   S_IFDIR, 'd'),
  (
   S_IFCHR, 'c'),
  (
   S_IFIFO, 'p')),
 (
  (
   S_IRUSR, 'r'),),
 (
  (
   S_IWUSR, 'w'),),
 (
  (
   S_IXUSR | S_ISUID, 's'),
  (
   S_ISUID, 'S'),
  (
   S_IXUSR, 'x')),
 (
  (
   S_IRGRP, 'r'),),
 (
  (
   S_IWGRP, 'w'),),
 (
  (
   S_IXGRP | S_ISGID, 's'),
  (
   S_ISGID, 'S'),
  (
   S_IXGRP, 'x')),
 (
  (
   S_IROTH, 'r'),),
 (
  (
   S_IWOTH, 'w'),),
 (
  (
   S_IXOTH | S_ISVTX, 't'),
  (
   S_ISVTX, 'T'),
  (
   S_IXOTH, 'x')))

def filemode(mode):
    perm = []
    for table in _filemode_table:
        for bit, char in table:
            if mode & bit == bit:
                perm.append(char)
                break
        else:
            perm.append('-')

    return ''.join(perm)


FILE_ATTRIBUTE_ARCHIVE = 32
FILE_ATTRIBUTE_COMPRESSED = 2048
FILE_ATTRIBUTE_DEVICE = 64
FILE_ATTRIBUTE_DIRECTORY = 16
FILE_ATTRIBUTE_ENCRYPTED = 16384
FILE_ATTRIBUTE_HIDDEN = 2
FILE_ATTRIBUTE_INTEGRITY_STREAM = 32768
FILE_ATTRIBUTE_NORMAL = 128
FILE_ATTRIBUTE_NOT_CONTENT_INDEXED = 8192
FILE_ATTRIBUTE_NO_SCRUB_DATA = 131072
FILE_ATTRIBUTE_OFFLINE = 4096
FILE_ATTRIBUTE_READONLY = 1
FILE_ATTRIBUTE_REPARSE_POINT = 1024
FILE_ATTRIBUTE_SPARSE_FILE = 512
FILE_ATTRIBUTE_SYSTEM = 4
FILE_ATTRIBUTE_TEMPORARY = 256
FILE_ATTRIBUTE_VIRTUAL = 65536
try:
    from _stat import *
except ImportError:
    pass