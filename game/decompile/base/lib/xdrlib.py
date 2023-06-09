# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xdrlib.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 6154 bytes
import struct
from io import BytesIO
from functools import wraps
__all__ = [
 'Error', 'Packer', 'Unpacker', 'ConversionError']

class Error(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return repr(self.msg)

    def __str__(self):
        return str(self.msg)


class ConversionError(Error):
    pass


def raise_conversion_error(function):

    @wraps(function)
    def result(self, value):
        try:
            return function(self, value)
        except struct.error as e:
            try:
                raise ConversionError(e.args[0]) from None
            finally:
                e = None
                del e

    return result


class Packer:

    def __init__(self):
        self.reset()

    def reset(self):
        self._Packer__buf = BytesIO()

    def get_buffer(self):
        return self._Packer__buf.getvalue()

    get_buf = get_buffer

    @raise_conversion_error
    def pack_uint(self, x):
        self._Packer__buf.write(struct.pack('>L', x))

    @raise_conversion_error
    def pack_int(self, x):
        self._Packer__buf.write(struct.pack('>l', x))

    pack_enum = pack_int

    def pack_bool(self, x):
        if x:
            self._Packer__buf.write(b'\x00\x00\x00\x01')
        else:
            self._Packer__buf.write(b'\x00\x00\x00\x00')

    def pack_uhyper(self, x):
        try:
            self.pack_uint(x >> 32 & 4294967295)
        except (TypeError, struct.error) as e:
            try:
                raise ConversionError(e.args[0]) from None
            finally:
                e = None
                del e

        try:
            self.pack_uint(x & 4294967295)
        except (TypeError, struct.error) as e:
            try:
                raise ConversionError(e.args[0]) from None
            finally:
                e = None
                del e

    pack_hyper = pack_uhyper

    @raise_conversion_error
    def pack_float(self, x):
        self._Packer__buf.write(struct.pack('>f', x))

    @raise_conversion_error
    def pack_double(self, x):
        self._Packer__buf.write(struct.pack('>d', x))

    def pack_fstring(self, n, s):
        if n < 0:
            raise ValueError('fstring size must be nonnegative')
        data = s[:n]
        n = (n + 3) // 4 * 4
        data = data + (n - len(data)) * b'\x00'
        self._Packer__buf.write(data)

    pack_fopaque = pack_fstring

    def pack_string(self, s):
        n = len(s)
        self.pack_uint(n)
        self.pack_fstring(n, s)

    pack_opaque = pack_string
    pack_bytes = pack_string

    def pack_list(self, list, pack_item):
        for item in list:
            self.pack_uint(1)
            pack_item(item)

        self.pack_uint(0)

    def pack_farray(self, n, list, pack_item):
        if len(list) != n:
            raise ValueError('wrong array size')
        for item in list:
            pack_item(item)

    def pack_array(self, list, pack_item):
        n = len(list)
        self.pack_uint(n)
        self.pack_farray(n, list, pack_item)


class Unpacker:

    def __init__(self, data):
        self.reset(data)

    def reset(self, data):
        self._Unpacker__buf = data
        self._Unpacker__pos = 0

    def get_position(self):
        return self._Unpacker__pos

    def set_position(self, position):
        self._Unpacker__pos = position

    def get_buffer(self):
        return self._Unpacker__buf

    def done(self):
        if self._Unpacker__pos < len(self._Unpacker__buf):
            raise Error('unextracted data remains')

    def unpack_uint(self):
        i = self._Unpacker__pos
        self._Unpacker__pos = j = i + 4
        data = self._Unpacker__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>L', data)[0]

    def unpack_int(self):
        i = self._Unpacker__pos
        self._Unpacker__pos = j = i + 4
        data = self._Unpacker__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>l', data)[0]

    unpack_enum = unpack_int

    def unpack_bool(self):
        return bool(self.unpack_int())

    def unpack_uhyper(self):
        hi = self.unpack_uint()
        lo = self.unpack_uint()
        return int(hi) << 32 | lo

    def unpack_hyper(self):
        x = self.unpack_uhyper()
        if x >= 9223372036854775808:
            x = x - 18446744073709551616
        return x

    def unpack_float(self):
        i = self._Unpacker__pos
        self._Unpacker__pos = j = i + 4
        data = self._Unpacker__buf[i:j]
        if len(data) < 4:
            raise EOFError
        return struct.unpack('>f', data)[0]

    def unpack_double(self):
        i = self._Unpacker__pos
        self._Unpacker__pos = j = i + 8
        data = self._Unpacker__buf[i:j]
        if len(data) < 8:
            raise EOFError
        return struct.unpack('>d', data)[0]

    def unpack_fstring(self, n):
        if n < 0:
            raise ValueError('fstring size must be nonnegative')
        i = self._Unpacker__pos
        j = i + (n + 3) // 4 * 4
        if j > len(self._Unpacker__buf):
            raise EOFError
        self._Unpacker__pos = j
        return self._Unpacker__buf[i:i + n]

    unpack_fopaque = unpack_fstring

    def unpack_string(self):
        n = self.unpack_uint()
        return self.unpack_fstring(n)

    unpack_opaque = unpack_string
    unpack_bytes = unpack_string

    def unpack_list(self, unpack_item):
        list = []
        while True:
            x = self.unpack_uint()
            if x == 0:
                break
            if x != 1:
                raise ConversionError('0 or 1 expected, got %r' % (x,))
            item = unpack_item()
            list.append(item)

        return list

    def unpack_farray(self, n, unpack_item):
        list = []
        for i in range(n):
            list.append(unpack_item())

        return list

    def unpack_array(self, unpack_item):
        n = self.unpack_uint()
        return self.unpack_farray(n, unpack_item)