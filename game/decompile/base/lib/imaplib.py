# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\imaplib.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 54636 bytes
__version__ = '2.58'
import binascii, errno, random, re, socket, subprocess, sys, time, calendar
from datetime import datetime, timezone, timedelta
from io import DEFAULT_BUFFER_SIZE
try:
    import ssl
    HAVE_SSL = True
except ImportError:
    HAVE_SSL = False

__all__ = ["'IMAP4'", "'IMAP4_stream'", "'Internaldate2tuple'", 
 "'Int2AP'", "'ParseFlags'", 
 "'Time2Internaldate'"]
CRLF = b'\r\n'
Debug = 0
IMAP4_PORT = 143
IMAP4_SSL_PORT = 993
AllowedVersions = ('IMAP4REV1', 'IMAP4')
_MAXLINE = 1000000
Commands = {
 'APPEND': ('AUTH', 'SELECTED'), 
 'AUTHENTICATE': 'NONAUTH', 
 'CAPABILITY': ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'), 
 'CHECK': 'SELECTED', 
 'CLOSE': 'SELECTED', 
 'COPY': 'SELECTED', 
 'CREATE': ('AUTH', 'SELECTED'), 
 'DELETE': ('AUTH', 'SELECTED'), 
 'DELETEACL': ('AUTH', 'SELECTED'), 
 'ENABLE': 'AUTH', 
 'EXAMINE': ('AUTH', 'SELECTED'), 
 'EXPUNGE': 'SELECTED', 
 'FETCH': 'SELECTED', 
 'GETACL': ('AUTH', 'SELECTED'), 
 'GETANNOTATION': ('AUTH', 'SELECTED'), 
 'GETQUOTA': ('AUTH', 'SELECTED'), 
 'GETQUOTAROOT': ('AUTH', 'SELECTED'), 
 'MYRIGHTS': ('AUTH', 'SELECTED'), 
 'LIST': ('AUTH', 'SELECTED'), 
 'LOGIN': 'NONAUTH', 
 'LOGOUT': ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'), 
 'LSUB': ('AUTH', 'SELECTED'), 
 'NAMESPACE': ('AUTH', 'SELECTED'), 
 'NOOP': ('NONAUTH', 'AUTH', 'SELECTED', 'LOGOUT'), 
 'PARTIAL': 'SELECTED', 
 'PROXYAUTH': 'AUTH', 
 'RENAME': ('AUTH', 'SELECTED'), 
 'SEARCH': 'SELECTED', 
 'SELECT': ('AUTH', 'SELECTED'), 
 'SETACL': ('AUTH', 'SELECTED'), 
 'SETANNOTATION': ('AUTH', 'SELECTED'), 
 'SETQUOTA': ('AUTH', 'SELECTED'), 
 'SORT': 'SELECTED', 
 'STARTTLS': 'NONAUTH', 
 'STATUS': ('AUTH', 'SELECTED'), 
 'STORE': 'SELECTED', 
 'SUBSCRIBE': ('AUTH', 'SELECTED'), 
 'THREAD': 'SELECTED', 
 'UID': 'SELECTED', 
 'UNSUBSCRIBE': ('AUTH', 'SELECTED')}
Continuation = re.compile(b'\\+( (?P<data>.*))?')
Flags = re.compile(b'.*FLAGS \\((?P<flags>[^\\)]*)\\)')
InternalDate = re.compile(b'.*INTERNALDATE "(?P<day>[ 0123][0-9])-(?P<mon>[A-Z][a-z][a-z])-(?P<year>[0-9][0-9][0-9][0-9]) (?P<hour>[0-9][0-9]):(?P<min>[0-9][0-9]):(?P<sec>[0-9][0-9]) (?P<zonen>[-+])(?P<zoneh>[0-9][0-9])(?P<zonem>[0-9][0-9])"')
Literal = re.compile(b'.*{(?P<size>\\d+)}$', re.ASCII)
MapCRLF = re.compile(b'\\r\\n|\\r|\\n')
Response_code = re.compile(b'\\[(?P<type>[A-Z-]+)( (?P<data>.*))?\\]')
Untagged_response = re.compile(b'\\* (?P<type>[A-Z-]+)( (?P<data>.*))?')
Untagged_status = re.compile(b'\\* (?P<data>\\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?', re.ASCII)
_Literal = b'.*{(?P<size>\\d+)}$'
_Untagged_status = b'\\* (?P<data>\\d+) (?P<type>[A-Z-]+)( (?P<data2>.*))?'

class IMAP4:

    class error(Exception):
        pass

    class abort(error):
        pass

    class readonly(abort):
        pass

    def __init__(self, host='', port=IMAP4_PORT):
        self.debug = Debug
        self.state = 'LOGOUT'
        self.literal = None
        self.tagged_commands = {}
        self.untagged_responses = {}
        self.continuation_response = ''
        self.is_readonly = False
        self.tagnum = 0
        self._tls_established = False
        self._mode_ascii()
        self.open(host, port)
        try:
            self._connect()
        except Exception:
            try:
                self.shutdown()
            except OSError:
                pass

            raise

    def _mode_ascii(self):
        self.utf8_enabled = False
        self._encoding = 'ascii'
        self.Literal = re.compile(_Literal, re.ASCII)
        self.Untagged_status = re.compile(_Untagged_status, re.ASCII)

    def _mode_utf8(self):
        self.utf8_enabled = True
        self._encoding = 'utf-8'
        self.Literal = re.compile(_Literal)
        self.Untagged_status = re.compile(_Untagged_status)

    def _connect(self):
        self.tagpre = Int2AP(random.randint(4096, 65535))
        self.tagre = re.compile(b'(?P<tag>' + self.tagpre + b'\\d+) (?P<type>[A-Z]+) (?P<data>.*)', re.ASCII)
        self.welcome = self._get_response()
        if 'PREAUTH' in self.untagged_responses:
            self.state = 'AUTH'
        else:
            if 'OK' in self.untagged_responses:
                self.state = 'NONAUTH'
            else:
                raise self.error(self.welcome)
        self._get_capabilities()
        for version in AllowedVersions:
            if version not in self.capabilities:
                continue
            self.PROTOCOL_VERSION = version
            return

        raise self.error('server not IMAP4 compliant')

    def __getattr__(self, attr):
        if attr in Commands:
            return getattr(self, attr.lower())
        raise AttributeError("Unknown IMAP4 command: '%s'" % attr)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        try:
            self.logout()
        except OSError:
            pass

    def _create_socket(self):
        return socket.create_connection((self.host, self.port))

    def open(self, host='', port=IMAP4_PORT):
        self.host = host
        self.port = port
        self.sock = self._create_socket()
        self.file = self.sock.makefile('rb')

    def read(self, size):
        return self.file.read(size)

    def readline(self):
        line = self.file.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise self.error('got more than %d bytes' % _MAXLINE)
        return line

    def send(self, data):
        self.sock.sendall(data)

    def shutdown(self):
        self.file.close()
        try:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError as exc:
                try:
                    if exc.errno != errno.ENOTCONN:
                        if getattr(exc, 'winerror', 0) != 10022:
                            raise
                finally:
                    exc = None
                    del exc

        finally:
            self.sock.close()

    def socket(self):
        return self.sock

    def recent(self):
        name = 'RECENT'
        typ, dat = self._untagged_response('OK', [None], name)
        if dat[-1]:
            return (
             typ, dat)
        typ, dat = self.noop()
        return self._untagged_response(typ, dat, name)

    def response(self, code):
        return self._untagged_response(code, [None], code.upper())

    def append(self, mailbox, flags, date_time, message):
        name = 'APPEND'
        if not mailbox:
            mailbox = 'INBOX'
        elif flags:
            if (
             flags[0], flags[-1]) != ('(', ')'):
                flags = '(%s)' % flags
            else:
                flags = None
            if date_time:
                date_time = Time2Internaldate(date_time)
        else:
            date_time = None
        literal = MapCRLF.sub(CRLF, message)
        if self.utf8_enabled:
            literal = b'UTF8 (' + literal + b')'
        self.literal = literal
        return self._simple_command(name, mailbox, flags, date_time)

    def authenticate(self, mechanism, authobject):
        mech = mechanism.upper()
        self.literal = _Authenticator(authobject).process
        typ, dat = self._simple_command('AUTHENTICATE', mech)
        if typ != 'OK':
            raise self.error(dat[-1].decode('utf-8', 'replace'))
        self.state = 'AUTH'
        return (typ, dat)

    def capability(self):
        name = 'CAPABILITY'
        typ, dat = self._simple_command(name)
        return self._untagged_response(typ, dat, name)

    def check(self):
        return self._simple_command('CHECK')

    def close(self):
        try:
            typ, dat = self._simple_command('CLOSE')
        finally:
            self.state = 'AUTH'

        return (
         typ, dat)

    def copy(self, message_set, new_mailbox):
        return self._simple_command('COPY', message_set, new_mailbox)

    def create(self, mailbox):
        return self._simple_command('CREATE', mailbox)

    def delete(self, mailbox):
        return self._simple_command('DELETE', mailbox)

    def deleteacl(self, mailbox, who):
        return self._simple_command('DELETEACL', mailbox, who)

    def enable(self, capability):
        if 'ENABLE' not in self.capabilities:
            raise IMAP4.error('Server does not support ENABLE')
        typ, data = self._simple_command('ENABLE', capability)
        if typ == 'OK':
            if 'UTF8=ACCEPT' in capability.upper():
                self._mode_utf8()
        return (
         typ, data)

    def expunge(self):
        name = 'EXPUNGE'
        typ, dat = self._simple_command(name)
        return self._untagged_response(typ, dat, name)

    def fetch(self, message_set, message_parts):
        name = 'FETCH'
        typ, dat = self._simple_command(name, message_set, message_parts)
        return self._untagged_response(typ, dat, name)

    def getacl(self, mailbox):
        typ, dat = self._simple_command('GETACL', mailbox)
        return self._untagged_response(typ, dat, 'ACL')

    def getannotation(self, mailbox, entry, attribute):
        typ, dat = self._simple_command('GETANNOTATION', mailbox, entry, attribute)
        return self._untagged_response(typ, dat, 'ANNOTATION')

    def getquota(self, root):
        typ, dat = self._simple_command('GETQUOTA', root)
        return self._untagged_response(typ, dat, 'QUOTA')

    def getquotaroot(self, mailbox):
        typ, dat = self._simple_command('GETQUOTAROOT', mailbox)
        typ, quota = self._untagged_response(typ, dat, 'QUOTA')
        typ, quotaroot = self._untagged_response(typ, dat, 'QUOTAROOT')
        return (typ, [quotaroot, quota])

    def list(self, directory='""', pattern='*'):
        name = 'LIST'
        typ, dat = self._simple_command(name, directory, pattern)
        return self._untagged_response(typ, dat, name)

    def login(self, user, password):
        typ, dat = self._simple_command('LOGIN', user, self._quote(password))
        if typ != 'OK':
            raise self.error(dat[-1])
        self.state = 'AUTH'
        return (typ, dat)

    def login_cram_md5(self, user, password):
        self.user, self.password = user, password
        return self.authenticate('CRAM-MD5', self._CRAM_MD5_AUTH)

    def _CRAM_MD5_AUTH(self, challenge):
        import hmac
        pwd = self.password.encode('utf-8') if isinstance(self.password, str) else self.password
        return self.user + ' ' + hmac.HMAC(pwd, challenge, 'md5').hexdigest()

    def logout(self):
        self.state = 'LOGOUT'
        try:
            typ, dat = self._simple_command('LOGOUT')
        except:
            typ, dat = 'NO', ['%s: %s' % sys.exc_info()[:2]]

        self.shutdown()
        if 'BYE' in self.untagged_responses:
            return (
             'BYE', self.untagged_responses['BYE'])
        return (
         typ, dat)

    def lsub(self, directory='""', pattern='*'):
        name = 'LSUB'
        typ, dat = self._simple_command(name, directory, pattern)
        return self._untagged_response(typ, dat, name)

    def myrights(self, mailbox):
        typ, dat = self._simple_command('MYRIGHTS', mailbox)
        return self._untagged_response(typ, dat, 'MYRIGHTS')

    def namespace(self):
        name = 'NAMESPACE'
        typ, dat = self._simple_command(name)
        return self._untagged_response(typ, dat, name)

    def noop(self):
        return self._simple_command('NOOP')

    def partial(self, message_num, message_part, start, length):
        name = 'PARTIAL'
        typ, dat = self._simple_command(name, message_num, message_part, start, length)
        return self._untagged_response(typ, dat, 'FETCH')

    def proxyauth(self, user):
        name = 'PROXYAUTH'
        return self._simple_command('PROXYAUTH', user)

    def rename(self, oldmailbox, newmailbox):
        return self._simple_command('RENAME', oldmailbox, newmailbox)

    def search(self, charset, *criteria):
        name = 'SEARCH'
        if charset:
            if self.utf8_enabled:
                raise IMAP4.error('Non-None charset not valid in UTF8 mode')
            typ, dat = (self._simple_command)(name, 'CHARSET', charset, *criteria)
        else:
            typ, dat = (self._simple_command)(name, *criteria)
        return self._untagged_response(typ, dat, name)

    def select(self, mailbox='INBOX', readonly=False):
        self.untagged_responses = {}
        self.is_readonly = readonly
        if readonly:
            name = 'EXAMINE'
        else:
            name = 'SELECT'
        typ, dat = self._simple_command(name, mailbox)
        if typ != 'OK':
            self.state = 'AUTH'
            return (typ, dat)
        self.state = 'SELECTED'
        if 'READ-ONLY' in self.untagged_responses:
            if not readonly:
                raise self.readonly('%s is not writable' % mailbox)
        return (
         typ, self.untagged_responses.get('EXISTS', [None]))

    def setacl(self, mailbox, who, what):
        return self._simple_command('SETACL', mailbox, who, what)

    def setannotation(self, *args):
        typ, dat = (self._simple_command)(*('SETANNOTATION', ), *args)
        return self._untagged_response(typ, dat, 'ANNOTATION')

    def setquota(self, root, limits):
        typ, dat = self._simple_command('SETQUOTA', root, limits)
        return self._untagged_response(typ, dat, 'QUOTA')

    def sort(self, sort_criteria, charset, *search_criteria):
        name = 'SORT'
        if (
         sort_criteria[0], sort_criteria[-1]) != ('(', ')'):
            sort_criteria = '(%s)' % sort_criteria
        typ, dat = (self._simple_command)(name, sort_criteria, charset, *search_criteria)
        return self._untagged_response(typ, dat, name)

    def starttls(self, ssl_context=None):
        name = 'STARTTLS'
        if not HAVE_SSL:
            raise self.error('SSL support missing')
        else:
            if self._tls_established:
                raise self.abort('TLS session already established')
            if name not in self.capabilities:
                raise self.abort('TLS not supported by server')
            if ssl_context is None:
                ssl_context = ssl._create_stdlib_context()
            typ, dat = self._simple_command(name)
            if typ == 'OK':
                self.sock = ssl_context.wrap_socket((self.sock), server_hostname=(self.host))
                self.file = self.sock.makefile('rb')
                self._tls_established = True
                self._get_capabilities()
            else:
                raise self.error("Couldn't establish TLS session")
        return self._untagged_response(typ, dat, name)

    def status(self, mailbox, names):
        name = 'STATUS'
        typ, dat = self._simple_command(name, mailbox, names)
        return self._untagged_response(typ, dat, name)

    def store(self, message_set, command, flags):
        if (
         flags[0], flags[-1]) != ('(', ')'):
            flags = '(%s)' % flags
        typ, dat = self._simple_command('STORE', message_set, command, flags)
        return self._untagged_response(typ, dat, 'FETCH')

    def subscribe(self, mailbox):
        return self._simple_command('SUBSCRIBE', mailbox)

    def thread(self, threading_algorithm, charset, *search_criteria):
        name = 'THREAD'
        typ, dat = (self._simple_command)(name, threading_algorithm, charset, *search_criteria)
        return self._untagged_response(typ, dat, name)

    def uid(self, command, *args):
        command = command.upper()
        if command not in Commands:
            raise self.error('Unknown IMAP4 UID command: %s' % command)
        else:
            if self.state not in Commands[command]:
                raise self.error('command %s illegal in state %s, only allowed in states %s' % (
                 command, self.state,
                 ', '.join(Commands[command])))
            name = 'UID'
            typ, dat = (self._simple_command)(name, command, *args)
            if command in ('SEARCH', 'SORT', 'THREAD'):
                name = command
            else:
                name = 'FETCH'
        return self._untagged_response(typ, dat, name)

    def unsubscribe(self, mailbox):
        return self._simple_command('UNSUBSCRIBE', mailbox)

    def xatom(self, name, *args):
        name = name.upper()
        if name not in Commands:
            Commands[name] = (
             self.state,)
        return (self._simple_command)(name, *args)

    def _append_untagged(self, typ, dat):
        if dat is None:
            dat = b''
        else:
            ur = self.untagged_responses
            if typ in ur:
                ur[typ].append(dat)
            else:
                ur[typ] = [
                 dat]

    def _check_bye(self):
        bye = self.untagged_responses.get('BYE')
        if bye:
            raise self.abort(bye[-1].decode(self._encoding, 'replace'))

    def _command(self, name, *args):
        if self.state not in Commands[name]:
            self.literal = None
            raise self.error('command %s illegal in state %s, only allowed in states %s' % (
             name, self.state,
             ', '.join(Commands[name])))
        else:
            for typ in ('OK', 'NO', 'BAD'):
                if typ in self.untagged_responses:
                    del self.untagged_responses[typ]

            if 'READ-ONLY' in self.untagged_responses:
                if not self.is_readonly:
                    raise self.readonly('mailbox status changed to READ-ONLY')
            tag = self._new_tag()
            name = bytes(name, self._encoding)
            data = tag + b' ' + name
            for arg in args:
                if arg is None:
                    continue
                if isinstance(arg, str):
                    arg = bytes(arg, self._encoding)
                data = data + b' ' + arg

            literal = self.literal
            if literal is not None:
                self.literal = None
                if type(literal) is type(self._command):
                    literator = literal
                else:
                    literator = None
                    data = data + bytes(' {%s}' % len(literal), self._encoding)
            try:
                self.send(data + CRLF)
            except OSError as val:
                try:
                    raise self.abort('socket error: %s' % val)
                finally:
                    val = None
                    del val

        if literal is None:
            return tag
        while 1:
            while self._get_response():
                if self.tagged_commands[tag]:
                    return tag

            if literator:
                literal = literator(self.continuation_response)
            try:
                self.send(literal)
                self.send(CRLF)
            except OSError as val:
                try:
                    raise self.abort('socket error: %s' % val)
                finally:
                    val = None
                    del val

            if not literator:
                break

        return tag

    def _command_complete(self, name, tag):
        if name != 'LOGOUT':
            self._check_bye()
        try:
            typ, data = self._get_tagged_response(tag)
        except self.abort as val:
            try:
                raise self.abort('command: %s => %s' % (name, val))
            finally:
                val = None
                del val

        except self.error as val:
            try:
                raise self.error('command: %s => %s' % (name, val))
            finally:
                val = None
                del val

        if name != 'LOGOUT':
            self._check_bye()
        if typ == 'BAD':
            raise self.error('%s command error: %s %s' % (name, typ, data))
        return (
         typ, data)

    def _get_capabilities(self):
        typ, dat = self.capability()
        if dat == [None]:
            raise self.error('no CAPABILITY response from server')
        dat = str(dat[-1], self._encoding)
        dat = dat.upper()
        self.capabilities = tuple(dat.split())

    def _get_response(self):
        resp = self._get_line()
        if self._match(self.tagre, resp):
            tag = self.mo.group('tag')
            if tag not in self.tagged_commands:
                raise self.abort('unexpected tagged response: %r' % resp)
            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            self.tagged_commands[tag] = (typ, [dat])
        else:
            dat2 = None
            if not self._match(Untagged_response, resp):
                if self._match(self.Untagged_status, resp):
                    dat2 = self.mo.group('data2')
            if self.mo is None:
                if self._match(Continuation, resp):
                    self.continuation_response = self.mo.group('data')
                    return
                raise self.abort('unexpected response: %r' % resp)
            typ = self.mo.group('type')
            typ = str(typ, self._encoding)
            dat = self.mo.group('data')
            if dat is None:
                dat = b''
            if dat2:
                dat = dat + b' ' + dat2
            while self._match(self.Literal, dat):
                size = int(self.mo.group('size'))
                data = self.read(size)
                self._append_untagged(typ, (dat, data))
                dat = self._get_line()

            self._append_untagged(typ, dat)
        if typ in ('OK', 'NO', 'BAD'):
            if self._match(Response_code, dat):
                typ = self.mo.group('type')
                typ = str(typ, self._encoding)
                self._append_untagged(typ, self.mo.group('data'))
        return resp

    def _get_tagged_response(self, tag):
        while True:
            result = self.tagged_commands[tag]
            if result is not None:
                del self.tagged_commands[tag]
                return result
            self._check_bye()
            try:
                self._get_response()
            except self.abort as val:
                try:
                    raise
                finally:
                    val = None
                    del val

    def _get_line(self):
        line = self.readline()
        if not line:
            raise self.abort('socket error: EOF')
        if not line.endswith(b'\r\n'):
            raise self.abort('socket error: unterminated line: %r' % line)
        line = line[:-2]
        return line

    def _match(self, cre, s):
        self.mo = cre.match(s)
        return self.mo is not None

    def _new_tag(self):
        tag = self.tagpre + bytes(str(self.tagnum), self._encoding)
        self.tagnum = self.tagnum + 1
        self.tagged_commands[tag] = None
        return tag

    def _quote(self, arg):
        arg = arg.replace('\\', '\\\\')
        arg = arg.replace('"', '\\"')
        return '"' + arg + '"'

    def _simple_command(self, name, *args):
        return self._command_complete(name, (self._command)(name, *args))

    def _untagged_response(self, typ, dat, name):
        if typ == 'NO':
            return (
             typ, dat)
        if name not in self.untagged_responses:
            return (
             typ, [None])
        data = self.untagged_responses.pop(name)
        return (
         typ, data)


if HAVE_SSL:

    class IMAP4_SSL(IMAP4):

        def __init__(self, host='', port=IMAP4_SSL_PORT, keyfile=None, certfile=None, ssl_context=None):
            if ssl_context is not None:
                if keyfile is not None:
                    raise ValueError('ssl_context and keyfile arguments are mutually exclusive')
            if ssl_context is not None:
                if certfile is not None:
                    raise ValueError('ssl_context and certfile arguments are mutually exclusive')
            if keyfile is not None or certfile is not None:
                import warnings
                warnings.warn('keyfile and certfile are deprecated, use acustom ssl_context instead', DeprecationWarning, 2)
            self.keyfile = keyfile
            self.certfile = certfile
            if ssl_context is None:
                ssl_context = ssl._create_stdlib_context(certfile=certfile, keyfile=keyfile)
            self.ssl_context = ssl_context
            IMAP4.__init__(self, host, port)

        def _create_socket(self):
            sock = IMAP4._create_socket(self)
            return self.ssl_context.wrap_socket(sock, server_hostname=(self.host))

        def open(self, host='', port=IMAP4_SSL_PORT):
            IMAP4.open(self, host, port)


    __all__.append('IMAP4_SSL')

class IMAP4_stream(IMAP4):

    def __init__(self, command):
        self.command = command
        IMAP4.__init__(self)

    def open(self, host=None, port=None):
        self.host = None
        self.port = None
        self.sock = None
        self.file = None
        self.process = subprocess.Popen((self.command), bufsize=DEFAULT_BUFFER_SIZE,
          stdin=(subprocess.PIPE),
          stdout=(subprocess.PIPE),
          shell=True,
          close_fds=True)
        self.writefile = self.process.stdin
        self.readfile = self.process.stdout

    def read(self, size):
        return self.readfile.read(size)

    def readline(self):
        return self.readfile.readline()

    def send(self, data):
        self.writefile.write(data)
        self.writefile.flush()

    def shutdown(self):
        self.readfile.close()
        self.writefile.close()
        self.process.wait()


class _Authenticator:

    def __init__(self, mechinst):
        self.mech = mechinst

    def process(self, data):
        ret = self.mech(self.decode(data))
        if ret is None:
            return b'*'
        return self.encode(ret)

    def encode(self, inp):
        oup = b''
        if isinstance(inp, str):
            inp = inp.encode('utf-8')
        while inp:
            if len(inp) > 48:
                t = inp[:48]
                inp = inp[48:]
            else:
                t = inp
                inp = b''
            e = binascii.b2a_base64(t)
            if e:
                oup = oup + e[:-1]

        return oup

    def decode(self, inp):
        if not inp:
            return b''
        return binascii.a2b_base64(inp)


Months = ' Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split(' ')
Mon2num = {s.encode(): n + 1 for n, s in enumerate(Months[1:])}

def Internaldate2tuple(resp):
    mo = InternalDate.match(resp)
    if not mo:
        return
    mon = Mon2num[mo.group('mon')]
    zonen = mo.group('zonen')
    day = int(mo.group('day'))
    year = int(mo.group('year'))
    hour = int(mo.group('hour'))
    min = int(mo.group('min'))
    sec = int(mo.group('sec'))
    zoneh = int(mo.group('zoneh'))
    zonem = int(mo.group('zonem'))
    zone = (zoneh * 60 + zonem) * 60
    if zonen == b'-':
        zone = -zone
    tt = (year, mon, day, hour, min, sec, -1, -1, -1)
    utc = calendar.timegm(tt) - zone
    return time.localtime(utc)


def Int2AP(num):
    val = b''
    AP = b'ABCDEFGHIJKLMNOP'
    num = int(abs(num))
    while num:
        num, mod = divmod(num, 16)
        val = AP[mod:mod + 1] + val

    return val


def ParseFlags(resp):
    mo = Flags.match(resp)
    if not mo:
        return ()
    return tuple(mo.group('flags').split())


def Time2Internaldate(date_time):
    if isinstance(date_time, (int, float)):
        dt = datetime.fromtimestamp(date_time, timezone.utc).astimezone()
    else:
        if isinstance(date_time, tuple):
            try:
                gmtoff = date_time.tm_gmtoff
            except AttributeError:
                if time.daylight:
                    dst = date_time[8]
                    if dst == -1:
                        dst = time.localtime(time.mktime(date_time))[8]
                    gmtoff = -(
                     time.timezone, time.altzone)[dst]
                else:
                    gmtoff = -time.timezone

            delta = timedelta(seconds=gmtoff)
            dt = datetime(*date_time[:6], **{'tzinfo': timezone(delta)})
        else:
            if isinstance(date_time, datetime):
                if date_time.tzinfo is None:
                    raise ValueError('date_time must be aware')
                dt = date_time
            else:
                if isinstance(date_time, str):
                    if (date_time[0], date_time[-1]) == ('"', '"'):
                        return date_time
                raise ValueError('date_time not of a known type')
    fmt = '"%d-{}-%Y %H:%M:%S %z"'.format(Months[dt.month])
    return dt.strftime(fmt)


if __name__ == '__main__':
    import getopt, getpass
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'd:s:')
    except getopt.error as val:
        try:
            optlist, args = ((), ())
        finally:
            val = None
            del val

    stream_command = None
    for opt, val in optlist:
        if opt == '-d':
            Debug = int(val)

    if not args:
        args = ('', )
    host = args[0]
    USER = getpass.getuser()
    PASSWD = getpass.getpass('IMAP password for %s on %s: ' % (USER, host or 'localhost'))
    test_mesg = 'From: %(user)s@localhost%(lf)sSubject: IMAP4 test%(lf)s%(lf)sdata...%(lf)s' % {'user':USER,  'lf':'\n'}
    test_seq1 = (
     (
      'login', (USER, PASSWD)),
     ('create', ('/tmp/xxx 1',)),
     ('rename', ('/tmp/xxx 1', '/tmp/yyy')),
     ('CREATE', ('/tmp/yyz 2',)),
     (
      'append', ('/tmp/yyz 2', None, None, test_mesg)),
     ('list', ('/tmp', 'yy*')),
     ('select', ('/tmp/yyz 2',)),
     ('search', (None, 'SUBJECT', 'test')),
     ('fetch', ('1', '(FLAGS INTERNALDATE RFC822)')),
     ('store', ('1', 'FLAGS', '(\\Deleted)')),
     ('namespace', ()),
     ('expunge', ()),
     ('recent', ()),
     ('close', ()))
    test_seq2 = (
     ('select', ()),
     ('response', ('UIDVALIDITY',)),
     ('uid', ('SEARCH', 'ALL')),
     ('response', ('EXISTS',)),
     (
      'append', (None, None, None, test_mesg)),
     ('recent', ()),
     ('logout', ()))

    def run(cmd, args):
        M._mesg('%s %s' % (cmd, args))
        typ, dat = (getattr(M, cmd))(*args)
        M._mesg('%s => %s %s' % (cmd, typ, dat))
        if typ == 'NO':
            raise dat[0]
        return dat


    try:
        if stream_command:
            M = IMAP4_stream(stream_command)
        else:
            M = IMAP4(host)
        if M.state == 'AUTH':
            test_seq1 = test_seq1[1:]
        M._mesg('PROTOCOL_VERSION = %s' % M.PROTOCOL_VERSION)
        M._mesg('CAPABILITIES = %r' % (M.capabilities,))
        for cmd, args in test_seq1:
            run(cmd, args)

        for ml in run('list', ('/tmp/', 'yy%')):
            mo = re.match('.*"([^"]+)"$', ml)
            if mo:
                path = mo.group(1)
            else:
                path = ml.split()[-1]
            run('delete', (path,))

        for cmd, args in test_seq2:
            dat = run(cmd, args)
            if (
             cmd, args) != ('uid', ('SEARCH', 'ALL')):
                continue
            uid = dat[-1].split()
            if not uid:
                continue
            run('uid', ('FETCH', '%s' % uid[-1],
             '(FLAGS INTERNALDATE RFC822.SIZE RFC822.HEADER RFC822.TEXT)'))

        print('\nAll tests OK.')
    except:
        print('\nTests failed.')
        if not Debug:
            print('\nIf you would like to see debugging output,\ntry: %s -d5\n' % sys.argv[0])
        raise