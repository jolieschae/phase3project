# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\genericpath.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 4907 bytes
import os, stat
__all__ = [
 "'commonprefix'", "'exists'", "'getatime'", "'getctime'", "'getmtime'", 
 "'getsize'", 
 "'isdir'", "'isfile'", "'samefile'", "'sameopenfile'", 
 "'samestat'"]

def exists(path):
    try:
        os.stat(path)
    except OSError:
        return False
    else:
        return True


def isfile(path):
    try:
        st = os.stat(path)
    except OSError:
        return False
    else:
        return stat.S_ISREG(st.st_mode)


def isdir(s):
    try:
        st = os.stat(s)
    except OSError:
        return False
    else:
        return stat.S_ISDIR(st.st_mode)


def getsize(filename):
    return os.stat(filename).st_size


def getmtime(filename):
    return os.stat(filename).st_mtime


def getatime(filename):
    return os.stat(filename).st_atime


def getctime(filename):
    return os.stat(filename).st_ctime


def commonprefix(m):
    if not m:
        return ''
    if not isinstance(m[0], (list, tuple)):
        m = tuple(map(os.fspath, m))
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]

    return s1


def samestat(s1, s2):
    return s1.st_ino == s2.st_ino and s1.st_dev == s2.st_dev


def samefile(f1, f2):
    s1 = os.stat(f1)
    s2 = os.stat(f2)
    return samestat(s1, s2)


def sameopenfile(fp1, fp2):
    s1 = os.fstat(fp1)
    s2 = os.fstat(fp2)
    return samestat(s1, s2)


def _splitext(p, sep, altsep, extsep):
    sepIndex = p.rfind(sep)
    if altsep:
        altsepIndex = p.rfind(altsep)
        sepIndex = max(sepIndex, altsepIndex)
    dotIndex = p.rfind(extsep)
    if dotIndex > sepIndex:
        filenameIndex = sepIndex + 1
        while filenameIndex < dotIndex:
            if p[filenameIndex:filenameIndex + 1] != extsep:
                return (
                 p[:dotIndex], p[dotIndex:])
            filenameIndex += 1

    return (
     p, p[:0])


def _check_arg_types(funcname, *args):
    hasstr = hasbytes = False
    for s in args:
        if isinstance(s, str):
            hasstr = True
        elif isinstance(s, bytes):
            hasbytes = True
        else:
            raise TypeError('%s() argument must be str or bytes, not %r' % (
             funcname, s.__class__.__name__)) from None

    if hasstr:
        if hasbytes:
            raise TypeError("Can't mix strings and bytes in path components") from None