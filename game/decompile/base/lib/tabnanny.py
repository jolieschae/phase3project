# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\tabnanny.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 11741 bytes
__version__ = '6'
import os, sys, tokenize
if not hasattr(tokenize, 'NL'):
    raise ValueError("tokenize.NL doesn't exist -- tokenize module too old")
__all__ = ['check', 'NannyNag', 'process_tokens']
verbose = 0
filename_only = 0

def errprint(*args):
    sep = ''
    for arg in args:
        sys.stderr.write(sep + str(arg))
        sep = ' '

    sys.stderr.write('\n')


def main():
    global filename_only
    global verbose
    import getopt
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'qv')
    except getopt.error as msg:
        try:
            errprint(msg)
            return
        finally:
            msg = None
            del msg

    for o, a in opts:
        if o == '-q':
            filename_only = filename_only + 1
        if o == '-v':
            verbose = verbose + 1

    if not args:
        errprint('Usage:', sys.argv[0], '[-v] file_or_directory ...')
        return
    for arg in args:
        check(arg)


class NannyNag(Exception):

    def __init__(self, lineno, msg, line):
        self.lineno, self.msg, self.line = lineno, msg, line

    def get_lineno(self):
        return self.lineno

    def get_msg(self):
        return self.msg

    def get_line(self):
        return self.line


def check(file):
    if os.path.isdir(file):
        if not os.path.islink(file):
            if verbose:
                print('%r: listing directory' % (file,))
            names = os.listdir(file)
            for name in names:
                fullname = os.path.join(file, name)
                if not os.path.isdir(fullname) or os.path.islink(fullname):
                    if os.path.normcase(name[-3:]) == '.py':
                        check(fullname)

            return
    try:
        f = tokenize.open(file)
    except OSError as msg:
        try:
            errprint('%r: I/O Error: %s' % (file, msg))
            return
        finally:
            msg = None
            del msg

    if verbose > 1:
        print('checking %r ...' % file)
    try:
        try:
            process_tokens(tokenize.generate_tokens(f.readline))
        except tokenize.TokenError as msg:
            try:
                errprint('%r: Token Error: %s' % (file, msg))
                return
            finally:
                msg = None
                del msg

        except IndentationError as msg:
            try:
                errprint('%r: Indentation Error: %s' % (file, msg))
                return
            finally:
                msg = None
                del msg

        except NannyNag as nag:
            try:
                badline = nag.get_lineno()
                line = nag.get_line()
                if verbose:
                    print('%r: *** Line %d: trouble in tab city! ***' % (file, badline))
                    print('offending line: %r' % (line,))
                    print(nag.get_msg())
                else:
                    if ' ' in file:
                        file = '"' + file + '"'
                    elif filename_only:
                        print(file)
                    else:
                        print(file, badline, repr(line))
                return
            finally:
                nag = None
                del nag

    finally:
        f.close()

    if verbose:
        print('%r: Clean bill of health.' % (file,))


class Whitespace:
    S, T = ' \t'

    def __init__(self, ws):
        self.raw = ws
        S, T = Whitespace.S, Whitespace.T
        count = []
        b = n = nt = 0
        for ch in self.raw:
            if ch == S:
                n = n + 1
                b = b + 1
            elif ch == T:
                n = n + 1
                nt = nt + 1
                if b >= len(count):
                    count = count + [0] * (b - len(count) + 1)
                count[b] = count[b] + 1
                b = 0
            else:
                break

        self.n = n
        self.nt = nt
        self.norm = (tuple(count), b)
        self.is_simple = len(count) <= 1

    def longest_run_of_spaces(self):
        count, trailing = self.norm
        return max(len(count) - 1, trailing)

    def indent_level(self, tabsize):
        count, trailing = self.norm
        il = 0
        for i in range(tabsize, len(count)):
            il = il + i // tabsize * count[i]

        return trailing + tabsize * (il + self.nt)

    def equal(self, other):
        return self.norm == other.norm

    def not_equal_witness(self, other):
        n = max(self.longest_run_of_spaces(), other.longest_run_of_spaces()) + 1
        a = []
        for ts in range(1, n + 1):
            if self.indent_level(ts) != other.indent_level(ts):
                a.append((ts,
                 self.indent_level(ts),
                 other.indent_level(ts)))

        return a

    def less(self, other):
        if self.n >= other.n:
            return False
        if self.is_simple:
            if other.is_simple:
                return self.nt <= other.nt
        n = max(self.longest_run_of_spaces(), other.longest_run_of_spaces()) + 1
        for ts in range(2, n + 1):
            if self.indent_level(ts) >= other.indent_level(ts):
                return False

        return True

    def not_less_witness(self, other):
        n = max(self.longest_run_of_spaces(), other.longest_run_of_spaces()) + 1
        a = []
        for ts in range(1, n + 1):
            if self.indent_level(ts) >= other.indent_level(ts):
                a.append((ts,
                 self.indent_level(ts),
                 other.indent_level(ts)))

        return a


def format_witnesses(w):
    firsts = (str(tup[0]) for tup in w)
    prefix = 'at tab size'
    if len(w) > 1:
        prefix = prefix + 's'
    return prefix + ' ' + ', '.join(firsts)


def process_tokens(tokens):
    INDENT = tokenize.INDENT
    DEDENT = tokenize.DEDENT
    NEWLINE = tokenize.NEWLINE
    JUNK = (tokenize.COMMENT, tokenize.NL)
    indents = [Whitespace('')]
    check_equal = 0
    for type, token, start, end, line in tokens:
        if type == NEWLINE:
            check_equal = 1
        elif type == INDENT:
            check_equal = 0
            thisguy = Whitespace(token)
            if not indents[-1].less(thisguy):
                witness = indents[-1].not_less_witness(thisguy)
                msg = 'indent not greater e.g. ' + format_witnesses(witness)
                raise NannyNag(start[0], msg, line)
            indents.append(thisguy)
        else:
            if type == DEDENT:
                check_equal = 1
                del indents[-1]


if __name__ == '__main__':
    main()