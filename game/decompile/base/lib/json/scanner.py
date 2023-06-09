# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\json\scanner.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 2498 bytes
import re
try:
    from _json import make_scanner as c_make_scanner
except ImportError:
    c_make_scanner = None

__all__ = ['make_scanner']
NUMBER_RE = re.compile('(-?(?:0|[1-9]\\d*))(\\.\\d+)?([eE][-+]?\\d+)?', re.VERBOSE | re.MULTILINE | re.DOTALL)

def py_make_scanner(context):
    parse_object = context.parse_object
    parse_array = context.parse_array
    parse_string = context.parse_string
    match_number = NUMBER_RE.match
    strict = context.strict
    parse_float = context.parse_float
    parse_int = context.parse_int
    parse_constant = context.parse_constant
    object_hook = context.object_hook
    object_pairs_hook = context.object_pairs_hook
    memo = context.memo

    def _scan_once(string, idx):
        try:
            nextchar = string[idx]
        except IndexError:
            raise StopIteration(idx) from None

        if nextchar == '"':
            return parse_string(string, idx + 1, strict)
        if nextchar == '{':
            return parse_object((string, idx + 1), strict, _scan_once, object_hook, object_pairs_hook, memo)
        if nextchar == '[':
            return parse_array((string, idx + 1), _scan_once)
        if nextchar == 'n':
            if string[idx:idx + 4] == 'null':
                return (
                 None, idx + 4)
        if nextchar == 't':
            if string[idx:idx + 4] == 'true':
                return (
                 True, idx + 4)
        if nextchar == 'f':
            if string[idx:idx + 5] == 'false':
                return (
                 False, idx + 5)
        m = match_number(string, idx)
        if m is not None:
            integer, frac, exp = m.groups()
            if frac or exp:
                res = parse_float(integer + (frac or '') + (exp or ''))
            else:
                res = parse_int(integer)
            return (
             res, m.end())
        if nextchar == 'N':
            if string[idx:idx + 3] == 'NaN':
                return (
                 parse_constant('NaN'), idx + 3)
        if nextchar == 'I':
            if string[idx:idx + 8] == 'Infinity':
                return (
                 parse_constant('Infinity'), idx + 8)
        if nextchar == '-':
            if string[idx:idx + 9] == '-Infinity':
                return (
                 parse_constant('-Infinity'), idx + 9)
        raise StopIteration(idx)

    def scan_once(string, idx):
        try:
            return _scan_once(string, idx)
        finally:
            memo.clear()

    return scan_once


make_scanner = c_make_scanner or py_make_scanner