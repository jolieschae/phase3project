# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\filecmp.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 10135 bytes
import os, stat
from itertools import filterfalse
__all__ = [
 "'clear_cache'", "'cmp'", "'dircmp'", "'cmpfiles'", "'DEFAULT_IGNORES'"]
_cache = {}
BUFSIZE = 8192
DEFAULT_IGNORES = [
 "'RCS'", "'CVS'", "'tags'", "'.git'", "'.hg'", "'.bzr'", "'_darcs'", "'__pycache__'"]

def clear_cache():
    _cache.clear()


def cmp(f1, f2, shallow=True):
    s1 = _sig(os.stat(f1))
    s2 = _sig(os.stat(f2))
    if s1[0] != stat.S_IFREG or s2[0] != stat.S_IFREG:
        return False
    if shallow:
        if s1 == s2:
            return True
    if s1[1] != s2[1]:
        return False
    outcome = _cache.get((f1, f2, s1, s2))
    if outcome is None:
        outcome = _do_cmp(f1, f2)
        if len(_cache) > 100:
            clear_cache()
        _cache[(f1, f2, s1, s2)] = outcome
    return outcome


def _sig(st):
    return (
     stat.S_IFMT(st.st_mode),
     st.st_size,
     st.st_mtime)


def _do_cmp(f1, f2):
    bufsize = BUFSIZE
    with open(f1, 'rb') as (fp1):
        with open(f2, 'rb') as (fp2):
            while 1:
                b1 = fp1.read(bufsize)
                b2 = fp2.read(bufsize)
                if b1 != b2:
                    return False
                if not b1:
                    return True


class dircmp:

    def __init__(self, a, b, ignore=None, hide=None):
        self.left = a
        self.right = b
        if hide is None:
            self.hide = [
             os.curdir, os.pardir]
        else:
            self.hide = hide
        if ignore is None:
            self.ignore = DEFAULT_IGNORES
        else:
            self.ignore = ignore

    def phase0(self):
        self.left_list = _filter(os.listdir(self.left), self.hide + self.ignore)
        self.right_list = _filter(os.listdir(self.right), self.hide + self.ignore)
        self.left_list.sort()
        self.right_list.sort()

    def phase1(self):
        a = dict(zip(map(os.path.normcase, self.left_list), self.left_list))
        b = dict(zip(map(os.path.normcase, self.right_list), self.right_list))
        self.common = list(map(a.__getitem__, filter(b.__contains__, a)))
        self.left_only = list(map(a.__getitem__, filterfalse(b.__contains__, a)))
        self.right_only = list(map(b.__getitem__, filterfalse(a.__contains__, b)))

    def phase2(self):
        self.common_dirs = []
        self.common_files = []
        self.common_funny = []
        for x in self.common:
            a_path = os.path.join(self.left, x)
            b_path = os.path.join(self.right, x)
            ok = 1
            try:
                a_stat = os.stat(a_path)
            except OSError as why:
                try:
                    ok = 0
                finally:
                    why = None
                    del why

            try:
                b_stat = os.stat(b_path)
            except OSError as why:
                try:
                    ok = 0
                finally:
                    why = None
                    del why

            if ok:
                a_type = stat.S_IFMT(a_stat.st_mode)
                b_type = stat.S_IFMT(b_stat.st_mode)
                if a_type != b_type:
                    self.common_funny.append(x)
                else:
                    if stat.S_ISDIR(a_type):
                        self.common_dirs.append(x)
                    else:
                        if stat.S_ISREG(a_type):
                            self.common_files.append(x)
                        else:
                            self.common_funny.append(x)
            else:
                self.common_funny.append(x)

    def phase3(self):
        xx = cmpfiles(self.left, self.right, self.common_files)
        self.same_files, self.diff_files, self.funny_files = xx

    def phase4(self):
        self.subdirs = {}
        for x in self.common_dirs:
            a_x = os.path.join(self.left, x)
            b_x = os.path.join(self.right, x)
            self.subdirs[x] = dircmp(a_x, b_x, self.ignore, self.hide)

    def phase4_closure(self):
        self.phase4()
        for sd in self.subdirs.values():
            sd.phase4_closure()

    def report(self):
        print('diff', self.left, self.right)
        if self.left_only:
            self.left_only.sort()
            print('Only in', self.left, ':', self.left_only)
        if self.right_only:
            self.right_only.sort()
            print('Only in', self.right, ':', self.right_only)
        if self.same_files:
            self.same_files.sort()
            print('Identical files :', self.same_files)
        if self.diff_files:
            self.diff_files.sort()
            print('Differing files :', self.diff_files)
        if self.funny_files:
            self.funny_files.sort()
            print('Trouble with common files :', self.funny_files)
        if self.common_dirs:
            self.common_dirs.sort()
            print('Common subdirectories :', self.common_dirs)
        if self.common_funny:
            self.common_funny.sort()
            print('Common funny cases :', self.common_funny)

    def report_partial_closure(self):
        self.report()
        for sd in self.subdirs.values():
            print()
            sd.report()

    def report_full_closure(self):
        self.report()
        for sd in self.subdirs.values():
            print()
            sd.report_full_closure()

    methodmap = dict(subdirs=phase4, same_files=phase3,
      diff_files=phase3,
      funny_files=phase3,
      common_dirs=phase2,
      common_files=phase2,
      common_funny=phase2,
      common=phase1,
      left_only=phase1,
      right_only=phase1,
      left_list=phase0,
      right_list=phase0)

    def __getattr__(self, attr):
        if attr not in self.methodmap:
            raise AttributeError(attr)
        self.methodmap[attr](self)
        return getattr(self, attr)


def cmpfiles(a, b, common, shallow=True):
    res = ([], [], [])
    for x in common:
        ax = os.path.join(a, x)
        bx = os.path.join(b, x)
        res[_cmp(ax, bx, shallow)].append(x)

    return res


def _cmp(a, b, sh, abs=abs, cmp=cmp):
    try:
        return not abs(cmp(a, b, sh))
    except OSError:
        return 2


def _filter(flist, skip):
    return list(filterfalse(skip.__contains__, flist))


def demo():
    import sys, getopt
    options, args = getopt.getopt(sys.argv[1:], 'r')
    if len(args) != 2:
        raise getopt.GetoptError('need exactly two args', None)
    else:
        dd = dircmp(args[0], args[1])
        if ('-r', '') in options:
            dd.report_full_closure()
        else:
            dd.report()


if __name__ == '__main__':
    demo()