# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\crypt.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 3449 bytes
import _crypt, string as _string
from random import SystemRandom as _SystemRandom
from collections import namedtuple as _namedtuple
_saltchars = _string.ascii_letters + _string.digits + './'
_sr = _SystemRandom()

class _Method(_namedtuple('_Method', 'name ident salt_chars total_size')):

    def __repr__(self):
        return '<crypt.METHOD_{}>'.format(self.name)


def mksalt(method=None, *, rounds=None):
    if method is None:
        method = methods[0]
    else:
        if rounds is not None:
            if not isinstance(rounds, int):
                raise TypeError(f"{rounds.__class__.__name__} object cannot be interpreted as an integer")
        if not method.ident:
            s = ''
        else:
            s = f"${method.ident}$"
    if method.ident and method.ident[0] == '2':
        if rounds is None:
            log_rounds = 12
        else:
            log_rounds = int.bit_length(rounds - 1)
            if rounds != 1 << log_rounds:
                raise ValueError('rounds must be a power of 2')
            if not 4 <= log_rounds <= 31:
                raise ValueError('rounds out of the range 2**4 to 2**31')
        s += f"{log_rounds:02d}$"
    else:
        if method.ident in ('5', '6'):
            if rounds is not None:
                if not 1000 <= rounds <= 999999999:
                    raise ValueError('rounds out of the range 1000 to 999_999_999')
                s += f"rounds={rounds}$"
        elif rounds is not None:
            raise ValueError(f"{method} doesn't support the rounds argument")
        s += ''.join((_sr.choice(_saltchars) for char in range(method.salt_chars)))
        return s


def crypt(word, salt=None):
    if salt is None or isinstance(salt, _Method):
        salt = mksalt(salt)
    return _crypt.crypt(word, salt)


methods = []

def _add_method(name, *args, rounds=None):
    method = _Method(name, *args)
    globals()['METHOD_' + name] = method
    salt = mksalt(method, rounds=rounds)
    result = crypt('', salt)
    if result:
        if len(result) == method.total_size:
            methods.append(method)
            return True
    return False


_add_method('SHA512', '6', 16, 106)
_add_method('SHA256', '5', 16, 63)
for _v in ('b', 'y', 'a', ''):
    if _add_method('BLOWFISH', ('2' + _v), 22, (59 + len(_v)), rounds=16):
        break

_add_method('MD5', '1', 8, 34)
_add_method('CRYPT', None, 2, 13)
del _v
del _add_method