# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\headerregistry.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 20813 bytes
from types import MappingProxyType
from email import utils
from email import errors
from email import _header_value_parser as parser

class Address:

    def __init__(self, display_name='', username='', domain='', addr_spec=None):
        if addr_spec is not None:
            if username or domain:
                raise TypeError('addrspec specified when username and/or domain also specified')
            a_s, rest = parser.get_addr_spec(addr_spec)
            if rest:
                raise ValueError("Invalid addr_spec; only '{}' could be parsed from '{}'".format(a_s, addr_spec))
            if a_s.all_defects:
                raise a_s.all_defects[0]
            username = a_s.local_part
            domain = a_s.domain
        self._display_name = display_name
        self._username = username
        self._domain = domain

    @property
    def display_name(self):
        return self._display_name

    @property
    def username(self):
        return self._username

    @property
    def domain(self):
        return self._domain

    @property
    def addr_spec(self):
        nameset = set(self.username)
        if len(nameset) > len(nameset - parser.DOT_ATOM_ENDS):
            lp = parser.quote_string(self.username)
        else:
            lp = self.username
        if self.domain:
            return lp + '@' + self.domain
        else:
            return lp or '<>'
        return lp

    def __repr__(self):
        return '{}(display_name={!r}, username={!r}, domain={!r})'.format(self.__class__.__name__, self.display_name, self.username, self.domain)

    def __str__(self):
        nameset = set(self.display_name)
        if len(nameset) > len(nameset - parser.SPECIALS):
            disp = parser.quote_string(self.display_name)
        else:
            disp = self.display_name
        if disp:
            addr_spec = '' if self.addr_spec == '<>' else self.addr_spec
            return '{} <{}>'.format(disp, addr_spec)
        return self.addr_spec

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.display_name == other.display_name and self.username == other.username and self.domain == other.domain


class Group:

    def __init__(self, display_name=None, addresses=None):
        self._display_name = display_name
        self._addresses = tuple(addresses) if addresses else tuple()

    @property
    def display_name(self):
        return self._display_name

    @property
    def addresses(self):
        return self._addresses

    def __repr__(self):
        return '{}(display_name={!r}, addresses={!r}'.format(self.__class__.__name__, self.display_name, self.addresses)

    def __str__(self):
        if self.display_name is None:
            if len(self.addresses) == 1:
                return str(self.addresses[0])
        disp = self.display_name
        if disp is not None:
            nameset = set(disp)
            if len(nameset) > len(nameset - parser.SPECIALS):
                disp = parser.quote_string(disp)
        adrstr = ', '.join((str(x) for x in self.addresses))
        adrstr = ' ' + adrstr if adrstr else adrstr
        return '{}:{};'.format(disp, adrstr)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.display_name == other.display_name and self.addresses == other.addresses


class BaseHeader(str):

    def __new__(cls, name, value):
        kwds = {'defects': []}
        cls.parse(value, kwds)
        if utils._has_surrogates(kwds['decoded']):
            kwds['decoded'] = utils._sanitize(kwds['decoded'])
        self = str.__new__(cls, kwds['decoded'])
        del kwds['decoded']
        (self.init)(name, **kwds)
        return self

    def init(self, name, *, parse_tree, defects):
        self._name = name
        self._parse_tree = parse_tree
        self._defects = defects

    @property
    def name(self):
        return self._name

    @property
    def defects(self):
        return tuple(self._defects)

    def __reduce__(self):
        return (
         _reconstruct_header,
         (
          self.__class__.__name__,
          self.__class__.__bases__,
          str(self)),
         self.__dict__)

    @classmethod
    def _reconstruct(cls, value):
        return str.__new__(cls, value)

    def fold(self, *, policy):
        header = parser.Header([
         parser.HeaderLabel([
          parser.ValueTerminal(self.name, 'header-name'),
          parser.ValueTerminal(':', 'header-sep')])])
        if self._parse_tree:
            header.append(parser.CFWSList([parser.WhiteSpaceTerminal(' ', 'fws')]))
        header.append(self._parse_tree)
        return header.fold(policy=policy)


def _reconstruct_header(cls_name, bases, value):
    return type(cls_name, bases, {})._reconstruct(value)


class UnstructuredHeader:
    max_count = None
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = cls.value_parser(value)
        kwds['decoded'] = str(kwds['parse_tree'])


class UniqueUnstructuredHeader(UnstructuredHeader):
    max_count = 1


class DateHeader:
    max_count = None
    value_parser = staticmethod(parser.get_unstructured)

    @classmethod
    def parse(cls, value, kwds):
        if not value:
            kwds['defects'].append(errors.HeaderMissingRequiredValue())
            kwds['datetime'] = None
            kwds['decoded'] = ''
            kwds['parse_tree'] = parser.TokenList()
            return
        if isinstance(value, str):
            value = utils.parsedate_to_datetime(value)
        kwds['datetime'] = value
        kwds['decoded'] = utils.format_datetime(kwds['datetime'])
        kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    def init(self, *args, **kw):
        self._datetime = kw.pop('datetime')
        (super().init)(*args, **kw)

    @property
    def datetime(self):
        return self._datetime


class UniqueDateHeader(DateHeader):
    max_count = 1


class AddressHeader:
    max_count = None

    @staticmethod
    def value_parser(value):
        address_list, value = parser.get_address_list(value)
        return address_list

    @classmethod
    def parse(cls, value, kwds):
        if isinstance(value, str):
            kwds['parse_tree'] = address_list = cls.value_parser(value)
            groups = []
            for addr in address_list.addresses:
                groups.append(Group(addr.display_name, [Address(mb.display_name or '', mb.local_part or '', mb.domain or '') for mb in addr.all_mailboxes]))

            defects = list(address_list.all_defects)
        else:
            if not hasattr(value, '__iter__'):
                value = [
                 value]
            groups = [Group(None, [item]) if not hasattr(item, 'addresses') else item for item in value]
            defects = []
        kwds['groups'] = groups
        kwds['defects'] = defects
        kwds['decoded'] = ', '.join([str(item) for item in groups])
        if 'parse_tree' not in kwds:
            kwds['parse_tree'] = cls.value_parser(kwds['decoded'])

    def init(self, *args, **kw):
        self._groups = tuple(kw.pop('groups'))
        self._addresses = None
        (super().init)(*args, **kw)

    @property
    def groups(self):
        return self._groups

    @property
    def addresses(self):
        if self._addresses is None:
            self._addresses = tuple((address for group in self._groups for address in group.addresses))
        return self._addresses


class UniqueAddressHeader(AddressHeader):
    max_count = 1


class SingleAddressHeader(AddressHeader):

    @property
    def address(self):
        if len(self.addresses) != 1:
            raise ValueError('value of single address header {} is not a single address'.format(self.name))
        return self.addresses[0]


class UniqueSingleAddressHeader(SingleAddressHeader):
    max_count = 1


class MIMEVersionHeader:
    max_count = 1
    value_parser = staticmethod(parser.parse_mime_version)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        kwds['major'] = None if parse_tree.minor is None else parse_tree.major
        kwds['minor'] = parse_tree.minor
        if parse_tree.minor is not None:
            kwds['version'] = '{}.{}'.format(kwds['major'], kwds['minor'])
        else:
            kwds['version'] = None

    def init(self, *args, **kw):
        self._version = kw.pop('version')
        self._major = kw.pop('major')
        self._minor = kw.pop('minor')
        (super().init)(*args, **kw)

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def version(self):
        return self._version


class ParameterizedMIMEHeader:
    max_count = 1

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)
        if parse_tree.params is None:
            kwds['params'] = {}
        else:
            kwds['params'] = {utils._sanitize(name).lower(): utils._sanitize(value) for name, value in parse_tree.params}

    def init(self, *args, **kw):
        self._params = kw.pop('params')
        (super().init)(*args, **kw)

    @property
    def params(self):
        return MappingProxyType(self._params)


class ContentTypeHeader(ParameterizedMIMEHeader):
    value_parser = staticmethod(parser.parse_content_type_header)

    def init(self, *args, **kw):
        (super().init)(*args, **kw)
        self._maintype = utils._sanitize(self._parse_tree.maintype)
        self._subtype = utils._sanitize(self._parse_tree.subtype)

    @property
    def maintype(self):
        return self._maintype

    @property
    def subtype(self):
        return self._subtype

    @property
    def content_type(self):
        return self.maintype + '/' + self.subtype


class ContentDispositionHeader(ParameterizedMIMEHeader):
    value_parser = staticmethod(parser.parse_content_disposition_header)

    def init(self, *args, **kw):
        (super().init)(*args, **kw)
        cd = self._parse_tree.content_disposition
        self._content_disposition = cd if cd is None else utils._sanitize(cd)

    @property
    def content_disposition(self):
        return self._content_disposition


class ContentTransferEncodingHeader:
    max_count = 1
    value_parser = staticmethod(parser.parse_content_transfer_encoding_header)

    @classmethod
    def parse(cls, value, kwds):
        kwds['parse_tree'] = parse_tree = cls.value_parser(value)
        kwds['decoded'] = str(parse_tree)
        kwds['defects'].extend(parse_tree.all_defects)

    def init(self, *args, **kw):
        (super().init)(*args, **kw)
        self._cte = utils._sanitize(self._parse_tree.cte)

    @property
    def cte(self):
        return self._cte


_default_header_map = {
 'subject': 'UniqueUnstructuredHeader', 
 'date': 'UniqueDateHeader', 
 'resent-date': 'DateHeader', 
 'orig-date': 'UniqueDateHeader', 
 'sender': 'UniqueSingleAddressHeader', 
 'resent-sender': 'SingleAddressHeader', 
 'to': 'UniqueAddressHeader', 
 'resent-to': 'AddressHeader', 
 'cc': 'UniqueAddressHeader', 
 'resent-cc': 'AddressHeader', 
 'bcc': 'UniqueAddressHeader', 
 'resent-bcc': 'AddressHeader', 
 'from': 'UniqueAddressHeader', 
 'resent-from': 'AddressHeader', 
 'reply-to': 'UniqueAddressHeader', 
 'mime-version': 'MIMEVersionHeader', 
 'content-type': 'ContentTypeHeader', 
 'content-disposition': 'ContentDispositionHeader', 
 'content-transfer-encoding': 'ContentTransferEncodingHeader'}

class HeaderRegistry:

    def __init__(self, base_class=BaseHeader, default_class=UnstructuredHeader, use_default_map=True):
        self.registry = {}
        self.base_class = base_class
        self.default_class = default_class
        if use_default_map:
            self.registry.update(_default_header_map)

    def map_to_type(self, name, cls):
        self.registry[name.lower()] = cls

    def __getitem__(self, name):
        cls = self.registry.get(name.lower(), self.default_class)
        return type('_' + cls.__name__, (cls, self.base_class), {})

    def __call__(self, name, value):
        return self[name](name, value)