# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\message.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 47883 bytes
__all__ = [
 'Message', 'EmailMessage']
import re, uu, quopri
from io import BytesIO, StringIO
from email import utils
from email import errors
from email._policybase import Policy, compat32
from email import charset as _charset
from email._encoded_words import decode_b
Charset = _charset.Charset
SEMISPACE = '; '
tspecials = re.compile('[ \\(\\)<>@,;:\\\\"/\\[\\]\\?=]')

def _splitparam(param):
    a, sep, b = str(param).partition(';')
    if not sep:
        return (
         a.strip(), None)
    return (
     a.strip(), b.strip())


def _formatparam(param, value=None, quote=True):
    if value is not None and len(value) > 0:
        if isinstance(value, tuple):
            param += '*'
            value = utils.encode_rfc2231(value[2], value[0], value[1])
            return '%s=%s' % (param, value)
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            param += '*'
            value = utils.encode_rfc2231(value, 'utf-8', '')
            return '%s=%s' % (param, value)
        else:
            if quote or tspecials.search(value):
                return '%s="%s"' % (param, utils.quote(value))
            return '%s=%s' % (param, value)
    else:
        return param


def _parseparam(s):
    s = ';' + str(s)
    plist = []
    while s[:1] == ';':
        s = s[1:]
        end = s.find(';')
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(';', end + 1)

        if end < 0:
            end = len(s)
        f = s[:end]
        if '=' in f:
            i = f.index('=')
            f = f[:i].strip().lower() + '=' + f[i + 1:].strip()
        plist.append(f.strip())
        s = s[end:]

    return plist


def _unquotevalue(value):
    if isinstance(value, tuple):
        return (
         value[0], value[1], utils.unquote(value[2]))
    return utils.unquote(value)


class Message:

    def __init__(self, policy=compat32):
        self.policy = policy
        self._headers = []
        self._unixfrom = None
        self._payload = None
        self._charset = None
        self.preamble = self.epilogue = None
        self.defects = []
        self._default_type = 'text/plain'

    def __str__(self):
        return self.as_string()

    def as_string(self, unixfrom=False, maxheaderlen=0, policy=None):
        from email.generator import Generator
        policy = self.policy if policy is None else policy
        fp = StringIO()
        g = Generator(fp, mangle_from_=False,
          maxheaderlen=maxheaderlen,
          policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()

    def __bytes__(self):
        return self.as_bytes()

    def as_bytes(self, unixfrom=False, policy=None):
        from email.generator import BytesGenerator
        policy = self.policy if policy is None else policy
        fp = BytesIO()
        g = BytesGenerator(fp, mangle_from_=False, policy=policy)
        g.flatten(self, unixfrom=unixfrom)
        return fp.getvalue()

    def is_multipart(self):
        return isinstance(self._payload, list)

    def set_unixfrom(self, unixfrom):
        self._unixfrom = unixfrom

    def get_unixfrom(self):
        return self._unixfrom

    def attach(self, payload):
        if self._payload is None:
            self._payload = [
             payload]
        else:
            try:
                self._payload.append(payload)
            except AttributeError:
                raise TypeError('Attach is not valid on a message with a non-multipart payload')

    def get_payload(self, i=None, decode=False):
        if self.is_multipart():
            if decode:
                return
            if i is None:
                return self._payload
        else:
            return self._payload[i]
            if i is not None:
                if not isinstance(self._payload, list):
                    raise TypeError('Expected list, got %s' % type(self._payload))
            payload = self._payload
            cte = str(self.get('content-transfer-encoding', '')).lower()
            if isinstance(payload, str):
                if utils._has_surrogates(payload):
                    bpayload = payload.encode('ascii', 'surrogateescape')
                    if not decode:
                        try:
                            payload = bpayload.decode(self.get_param('charset', 'ascii'), 'replace')
                        except LookupError:
                            payload = bpayload.decode('ascii', 'replace')

                elif decode:
                    try:
                        bpayload = payload.encode('ascii')
                    except UnicodeError:
                        bpayload = payload.encode('raw-unicode-escape')

            return decode or payload
        if cte == 'quoted-printable':
            return quopri.decodestring(bpayload)
        if cte == 'base64':
            value, defects = decode_b((b'').join(bpayload.splitlines()))
            for defect in defects:
                self.policy.handle_defect(self, defect)

            return value
        if cte in ('x-uuencode', 'uuencode', 'uue', 'x-uue'):
            in_file = BytesIO(bpayload)
            out_file = BytesIO()
            try:
                uu.decode(in_file, out_file, quiet=True)
                return out_file.getvalue()
            except uu.Error:
                return bpayload

        if isinstance(payload, str):
            return bpayload
        return payload

    def set_payload(self, payload, charset=None):
        if hasattr(payload, 'encode'):
            if charset is None:
                self._payload = payload
                return
            if not isinstance(charset, Charset):
                charset = Charset(charset)
            payload = payload.encode(charset.output_charset)
        elif hasattr(payload, 'decode'):
            self._payload = payload.decode('ascii', 'surrogateescape')
        else:
            self._payload = payload
        if charset is not None:
            self.set_charset(charset)

    def set_charset(self, charset):
        if charset is None:
            self.del_param('charset')
            self._charset = None
            return
            if not isinstance(charset, Charset):
                charset = Charset(charset)
            else:
                self._charset = charset
                if 'MIME-Version' not in self:
                    self.add_header('MIME-Version', '1.0')
                if 'Content-Type' not in self:
                    self.add_header('Content-Type', 'text/plain', charset=(charset.get_output_charset()))
                else:
                    self.set_param('charset', charset.get_output_charset())
            if charset != charset.get_output_charset():
                self._payload = charset.body_encode(self._payload)
        elif 'Content-Transfer-Encoding' not in self:
            cte = charset.get_body_encoding()
            try:
                cte(self)
            except TypeError:
                payload = self._payload
                if payload:
                    try:
                        payload = payload.encode('ascii', 'surrogateescape')
                    except UnicodeError:
                        payload = payload.encode(charset.output_charset)

                self._payload = charset.body_encode(payload)
                self.add_header('Content-Transfer-Encoding', cte)

    def get_charset(self):
        return self._charset

    def __len__(self):
        return len(self._headers)

    def __getitem__(self, name):
        return self.get(name)

    def __setitem__(self, name, val):
        max_count = self.policy.header_max_count(name)
        if max_count:
            lname = name.lower()
            found = 0
            for k, v in self._headers:
                if k.lower() == lname:
                    found += 1
                    if found >= max_count:
                        raise ValueError('There may be at most {} {} headers in a message'.format(max_count, name))

        self._headers.append(self.policy.header_store_parse(name, val))

    def __delitem__(self, name):
        name = name.lower()
        newheaders = []
        for k, v in self._headers:
            if k.lower() != name:
                newheaders.append((k, v))

        self._headers = newheaders

    def __contains__(self, name):
        return name.lower() in [k.lower() for k, v in self._headers]

    def __iter__(self):
        for field, value in self._headers:
            yield field

    def keys(self):
        return [k for k, v in self._headers]

    def values(self):
        return [self.policy.header_fetch_parse(k, v) for k, v in self._headers]

    def items(self):
        return [(k, self.policy.header_fetch_parse(k, v)) for k, v in self._headers]

    def get(self, name, failobj=None):
        name = name.lower()
        for k, v in self._headers:
            if k.lower() == name:
                return self.policy.header_fetch_parse(k, v)

        return failobj

    def set_raw(self, name, value):
        self._headers.append((name, value))

    def raw_items(self):
        return iter(self._headers.copy())

    def get_all(self, name, failobj=None):
        values = []
        name = name.lower()
        for k, v in self._headers:
            if k.lower() == name:
                values.append(self.policy.header_fetch_parse(k, v))

        if not values:
            return failobj
        return values

    def add_header(self, _name, _value, **_params):
        parts = []
        for k, v in _params.items():
            if v is None:
                parts.append(k.replace('_', '-'))
            else:
                parts.append(_formatparam(k.replace('_', '-'), v))

        if _value is not None:
            parts.insert(0, _value)
        self[_name] = SEMISPACE.join(parts)

    def replace_header(self, _name, _value):
        _name = _name.lower()
        for i, (k, v) in zip(range(len(self._headers)), self._headers):
            if k.lower() == _name:
                self._headers[i] = self.policy.header_store_parse(k, _value)
                break
        else:
            raise KeyError(_name)

    def get_content_type(self):
        missing = object()
        value = self.get('content-type', missing)
        if value is missing:
            return self.get_default_type()
        ctype = _splitparam(value)[0].lower()
        if ctype.count('/') != 1:
            return 'text/plain'
        return ctype

    def get_content_maintype(self):
        ctype = self.get_content_type()
        return ctype.split('/')[0]

    def get_content_subtype(self):
        ctype = self.get_content_type()
        return ctype.split('/')[1]

    def get_default_type(self):
        return self._default_type

    def set_default_type(self, ctype):
        self._default_type = ctype

    def _get_params_preserve(self, failobj, header):
        missing = object()
        value = self.get(header, missing)
        if value is missing:
            return failobj
        params = []
        for p in _parseparam(value):
            try:
                name, val = p.split('=', 1)
                name = name.strip()
                val = val.strip()
            except ValueError:
                name = p.strip()
                val = ''

            params.append((name, val))

        params = utils.decode_params(params)
        return params

    def get_params(self, failobj=None, header='content-type', unquote=True):
        missing = object()
        params = self._get_params_preserve(missing, header)
        if params is missing:
            return failobj
        if unquote:
            return [(k, _unquotevalue(v)) for k, v in params]
        return params

    def get_param(self, param, failobj=None, header='content-type', unquote=True):
        if header not in self:
            return failobj
        for k, v in self._get_params_preserve(failobj, header):
            if k.lower() == param.lower():
                if unquote:
                    return _unquotevalue(v)
                return v

        return failobj

    def set_param(self, param, value, header='Content-Type', requote=True, charset=None, language='', replace=False):
        if not isinstance(value, tuple):
            if charset:
                value = (
                 charset, language, value)
            elif header not in self:
                if header.lower() == 'content-type':
                    ctype = 'text/plain'
                else:
                    ctype = self.get(header)
                if not self.get_param(param, header=header):
                    if not ctype:
                        ctype = _formatparam(param, value, requote)
                    else:
                        ctype = SEMISPACE.join([
                         ctype, _formatparam(param, value, requote)])
            else:
                ctype = ''
                for old_param, old_value in self.get_params(header=header, unquote=requote):
                    append_param = ''
                    if old_param.lower() == param.lower():
                        append_param = _formatparam(param, value, requote)
                    else:
                        append_param = _formatparam(old_param, old_value, requote)
                    if not ctype:
                        ctype = append_param
                    else:
                        ctype = SEMISPACE.join([ctype, append_param])

            if ctype != self.get(header):
                if replace:
                    self.replace_header(header, ctype)
        else:
            del self[header]
            self[header] = ctype

    def del_param(self, param, header='content-type', requote=True):
        if header not in self:
            return
        new_ctype = ''
        for p, v in self.get_params(header=header, unquote=requote):
            if p.lower() != param.lower():
                if not new_ctype:
                    new_ctype = _formatparam(p, v, requote)
                else:
                    new_ctype = SEMISPACE.join([new_ctype,
                     _formatparam(p, v, requote)])

        if new_ctype != self.get(header):
            del self[header]
            self[header] = new_ctype

    def set_type(self, type, header='Content-Type', requote=True):
        if not type.count('/') == 1:
            raise ValueError
        if header.lower() == 'content-type':
            del self['mime-version']
            self['MIME-Version'] = '1.0'
        if header not in self:
            self[header] = type
            return
        params = self.get_params(header=header, unquote=requote)
        del self[header]
        self[header] = type
        for p, v in params[1:]:
            self.set_param(p, v, header, requote)

    def get_filename(self, failobj=None):
        missing = object()
        filename = self.get_param('filename', missing, 'content-disposition')
        if filename is missing:
            filename = self.get_param('name', missing, 'content-type')
        if filename is missing:
            return failobj
        return utils.collapse_rfc2231_value(filename).strip()

    def get_boundary(self, failobj=None):
        missing = object()
        boundary = self.get_param('boundary', missing)
        if boundary is missing:
            return failobj
        return utils.collapse_rfc2231_value(boundary).rstrip()

    def set_boundary(self, boundary):
        missing = object()
        params = self._get_params_preserve(missing, 'content-type')
        if params is missing:
            raise errors.HeaderParseError('No Content-Type header found')
        newparams = []
        foundp = False
        for pk, pv in params:
            if pk.lower() == 'boundary':
                newparams.append(('boundary', '"%s"' % boundary))
                foundp = True
            else:
                newparams.append((pk, pv))

        if not foundp:
            newparams.append(('boundary', '"%s"' % boundary))
        newheaders = []
        for h, v in self._headers:
            if h.lower() == 'content-type':
                parts = []
                for k, v in newparams:
                    if v == '':
                        parts.append(k)
                    else:
                        parts.append('%s=%s' % (k, v))

                val = SEMISPACE.join(parts)
                newheaders.append(self.policy.header_store_parse(h, val))
            else:
                newheaders.append((h, v))

        self._headers = newheaders

    def get_content_charset(self, failobj=None):
        missing = object()
        charset = self.get_param('charset', missing)
        if charset is missing:
            return failobj
        if isinstance(charset, tuple):
            pcharset = charset[0] or 'us-ascii'
            try:
                as_bytes = charset[2].encode('raw-unicode-escape')
                charset = str(as_bytes, pcharset)
            except (LookupError, UnicodeError):
                charset = charset[2]

        try:
            charset.encode('us-ascii')
        except UnicodeError:
            return failobj
        else:
            return charset.lower()

    def get_charsets(self, failobj=None):
        return [part.get_content_charset(failobj) for part in self.walk()]

    def get_content_disposition(self):
        value = self.get('content-disposition')
        if value is None:
            return
        c_d = _splitparam(value)[0].lower()
        return c_d

    from email.iterators import walk


class MIMEPart(Message):

    def __init__(self, policy=None):
        if policy is None:
            from email.policy import default
            policy = default
        Message.__init__(self, policy)

    def as_string(self, unixfrom=False, maxheaderlen=None, policy=None):
        policy = self.policy if policy is None else policy
        if maxheaderlen is None:
            maxheaderlen = policy.max_line_length
        return super().as_string(maxheaderlen=maxheaderlen, policy=policy)

    def __str__(self):
        return self.as_string(policy=self.policy.clone(utf8=True))

    def is_attachment(self):
        c_d = self.get('content-disposition')
        if c_d is None:
            return False
        return c_d.content_disposition == 'attachment'

    def _find_body(self, part, preferencelist):
        if part.is_attachment():
            return
        maintype, subtype = part.get_content_type().split('/')
        if maintype == 'text':
            if subtype in preferencelist:
                yield (
                 preferencelist.index(subtype), part)
            return
        if maintype != 'multipart':
            return
        if subtype != 'related':
            for subpart in part.iter_parts():
                yield from self._find_body(subpart, preferencelist)

            return
        if 'related' in preferencelist:
            yield (
             preferencelist.index('related'), part)
        candidate = None
        start = part.get_param('start')
        if start:
            for subpart in part.iter_parts():
                if subpart['content-id'] == start:
                    candidate = subpart
                    break

        if candidate is None:
            subparts = part.get_payload()
            candidate = subparts[0] if subparts else None
        if candidate is not None:
            yield from self._find_body(candidate, preferencelist)

    def get_body(self, preferencelist=('related', 'html', 'plain')):
        best_prio = len(preferencelist)
        body = None
        for prio, part in self._find_body(self, preferencelist):
            if prio < best_prio:
                best_prio = prio
                body = part
                if prio == 0:
                    break

        return body

    _body_types = {
     ('text', 'plain'),
     ('text', 'html'),
     ('multipart', 'related'),
     ('multipart', 'alternative')}

    def iter_attachments(self):
        maintype, subtype = self.get_content_type().split('/')
        if maintype != 'multipart' or subtype == 'alternative':
            return
        parts = self.get_payload().copy()
        if maintype == 'multipart':
            if subtype == 'related':
                start = self.get_param('start')
                if start:
                    found = False
                    attachments = []
                    for part in parts:
                        if part.get('content-id') == start:
                            found = True
                        else:
                            attachments.append(part)

                    if found:
                        yield from attachments
                        return
                parts.pop(0)
                yield from parts
                return
        seen = []
        for part in parts:
            maintype, subtype = part.get_content_type().split('/')
            if (maintype, subtype) in self._body_types:
                if not part.is_attachment():
                    if subtype not in seen:
                        seen.append(subtype)
                        continue
            yield part

    def iter_parts(self):
        if self.get_content_maintype() == 'multipart':
            yield from self.get_payload()
        if False:
            yield None

    def get_content(self, *args, content_manager=None, **kw):
        if content_manager is None:
            content_manager = self.policy.content_manager
        return (content_manager.get_content)(self, *args, **kw)

    def set_content(self, *args, content_manager=None, **kw):
        if content_manager is None:
            content_manager = self.policy.content_manager
        (content_manager.set_content)(self, *args, **kw)

    def _make_multipart(self, subtype, disallowed_subtypes, boundary):
        if self.get_content_maintype() == 'multipart':
            existing_subtype = self.get_content_subtype()
            disallowed_subtypes = disallowed_subtypes + (subtype,)
            if existing_subtype in disallowed_subtypes:
                raise ValueError('Cannot convert {} to {}'.format(existing_subtype, subtype))
        else:
            keep_headers = []
            part_headers = []
            for name, value in self._headers:
                if name.lower().startswith('content-'):
                    part_headers.append((name, value))
                else:
                    keep_headers.append((name, value))

            if part_headers:
                part = type(self)(policy=(self.policy))
                part._headers = part_headers
                part._payload = self._payload
                self._payload = [part]
            else:
                self._payload = []
        self._headers = keep_headers
        self['Content-Type'] = 'multipart/' + subtype
        if boundary is not None:
            self.set_param('boundary', boundary)

    def make_related(self, boundary=None):
        self._make_multipart('related', ('alternative', 'mixed'), boundary)

    def make_alternative(self, boundary=None):
        self._make_multipart('alternative', ('mixed', ), boundary)

    def make_mixed(self, boundary=None):
        self._make_multipart('mixed', (), boundary)

    def _add_multipart(self, _subtype, *args, _disp=None, **kw):
        if self.get_content_maintype() != 'multipart' or self.get_content_subtype() != _subtype:
            getattr(self, 'make_' + _subtype)()
        part = type(self)(policy=(self.policy))
        (part.set_content)(*args, **kw)
        if _disp:
            if 'content-disposition' not in part:
                part['Content-Disposition'] = _disp
        self.attach(part)

    def add_related(self, *args, **kw):
        (self._add_multipart)(*('related', ), *args, _disp='inline', **kw)

    def add_alternative(self, *args, **kw):
        (self._add_multipart)('alternative', *args, **kw)

    def add_attachment(self, *args, **kw):
        (self._add_multipart)(*('mixed', ), *args, _disp='attachment', **kw)

    def clear(self):
        self._headers = []
        self._payload = None

    def clear_content(self):
        self._headers = [(n, v) for n, v in self._headers if not n.lower().startswith('content-')]
        self._payload = None


class EmailMessage(MIMEPart):

    def set_content(self, *args, **kw):
        (super().set_content)(*args, **kw)
        if 'MIME-Version' not in self:
            self['MIME-Version'] = '1.0'