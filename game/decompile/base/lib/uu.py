# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\uu.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 7100 bytes
import binascii, os, sys
__all__ = [
 'Error', 'encode', 'decode']

class Error(Exception):
    pass


def encode(in_file, out_file, name=None, mode=None, *, backtick=False):
    opened_files = []
    try:
        if in_file == '-':
            in_file = sys.stdin.buffer
        else:
            if isinstance(in_file, str):
                if name is None:
                    name = os.path.basename(in_file)
            else:
                if mode is None:
                    try:
                        mode = os.stat(in_file).st_mode
                    except AttributeError:
                        pass

                    in_file = open(in_file, 'rb')
                    opened_files.append(in_file)
                elif out_file == '-':
                    out_file = sys.stdout.buffer
                else:
                    if isinstance(out_file, str):
                        out_file = open(out_file, 'wb')
                        opened_files.append(out_file)
                if name is None:
                    name = '-'
                if mode is None:
                    mode = 438
                out_file.write(('begin %o %s\n' % (mode & 511, name)).encode('ascii'))
                data = in_file.read(45)
                while len(data) > 0:
                    out_file.write(binascii.b2a_uu(data, backtick=backtick))
                    data = in_file.read(45)

                if backtick:
                    out_file.write(b'`\nend\n')
                else:
                    out_file.write(b' \nend\n')
    finally:
        for f in opened_files:
            f.close()


def decode(in_file, out_file=None, mode=None, quiet=False):
    opened_files = []
    if in_file == '-':
        in_file = sys.stdin.buffer
    else:
        if isinstance(in_file, str):
            in_file = open(in_file, 'rb')
            opened_files.append(in_file)
    try:
        while 1:
            hdr = in_file.readline()
            if not hdr:
                raise Error('No valid begin line found in input file')
            if not hdr.startswith(b'begin'):
                continue
            hdrfields = hdr.split(b' ', 2)
            if len(hdrfields) == 3 and hdrfields[0] == b'begin':
                try:
                    int(hdrfields[1], 8)
                    break
                except ValueError:
                    pass

        if out_file is None:
            out_file = hdrfields[2].rstrip(b' \t\r\n\x0c').decode('ascii')
            if os.path.exists(out_file):
                raise Error('Cannot overwrite existing file: %s' % out_file)
        if mode is None:
            mode = int(hdrfields[1], 8)
        if out_file == '-':
            out_file = sys.stdout.buffer
        else:
            if isinstance(out_file, str):
                fp = open(out_file, 'wb')
                try:
                    os.path.chmod(out_file, mode)
                except AttributeError:
                    pass

                out_file = fp
                opened_files.append(out_file)
            s = in_file.readline()
            while s and s.strip(b' \t\r\n\x0c') != b'end':
                try:
                    data = binascii.a2b_uu(s)
                except binascii.Error as v:
                    try:
                        nbytes = ((s[0] - 32 & 63) * 4 + 5) // 3
                        data = binascii.a2b_uu(s[:nbytes])
                        if not quiet:
                            sys.stderr.write('Warning: %s\n' % v)
                    finally:
                        v = None
                        del v

                out_file.write(data)
                s = in_file.readline()

            if not s:
                raise Error('Truncated input file')
    finally:
        for f in opened_files:
            f.close()


def test():
    import optparse
    parser = optparse.OptionParser(usage='usage: %prog [-d] [-t] [input [output]]')
    parser.add_option('-d', '--decode', dest='decode', help='Decode (instead of encode)?', default=False, action='store_true')
    parser.add_option('-t', '--text', dest='text', help='data is text, encoded format unix-compatible text?', default=False, action='store_true')
    options, args = parser.parse_args()
    if len(args) > 2:
        parser.error('incorrect number of arguments')
        sys.exit(1)
    input = sys.stdin.buffer
    output = sys.stdout.buffer
    if len(args) > 0:
        input = args[0]
    if len(args) > 1:
        output = args[1]
    if options.decode:
        if options.text:
            if isinstance(output, str):
                output = open(output, 'wb')
            else:
                print(sys.argv[0], ': cannot do -t to stdout')
                sys.exit(1)
        decode(input, output)
    else:
        if options.text:
            if isinstance(input, str):
                input = open(input, 'rb')
            else:
                print(sys.argv[0], ': cannot do -t from stdin')
                sys.exit(1)
        encode(input, output)


if __name__ == '__main__':
    test()