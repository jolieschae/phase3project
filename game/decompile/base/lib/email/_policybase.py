# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\email\_policybase.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 15447 bytes
import abc
from email import header
from email import charset as _charset
from email.utils import _has_surrogates
__all__ = [
 'Policy',
 'Compat32',
 'compat32']

class _PolicyBase:

    def __init__(self, **kw):
        for name, value in kw.items():
            if hasattr(self, name):
                super(_PolicyBase, self).__setattr__(name, value)
            else:
                raise TypeError('{!r} is an invalid keyword argument for {}'.format(name, self.__class__.__name__))

    def __repr__(self):
        args = ['{}={!r}'.format(name, value) for name, value in self.__dict__.items()]
        return '{}({})'.format(self.__class__.__name__, ', '.join(args))

    def clone(self, **kw):
        newpolicy = self.__class__.__new__(self.__class__)
        for attr, value in self.__dict__.items():
            object.__setattr__(newpolicy, attr, value)

        for attr, value in kw.items():
            if not hasattr(self, attr):
                raise TypeError('{!r} is an invalid keyword argument for {}'.format(attr, self.__class__.__name__))
            object.__setattr__(newpolicy, attr, value)

        return newpolicy

    def __setattr__(self, name, value):
        if hasattr(self, name):
            msg = '{!r} object attribute {!r} is read-only'
        else:
            msg = '{!r} object has no attribute {!r}'
        raise AttributeError(msg.format(self.__class__.__name__, name))

    def __add__(self, other):
        return (self.clone)(**other.__dict__)


def _append_doc(doc, added_doc):
    doc = doc.rsplit('\n', 1)[0]
    added_doc = added_doc.split('\n', 1)[1]
    return doc + '\n' + added_doc


def _extend_docstrings(cls):
    if cls.__doc__:
        if cls.__doc__.startswith('+'):
            cls.__doc__ = _append_doc(cls.__bases__[0].__doc__, cls.__doc__)
    for name, attr in cls.__dict__.items():
        if attr.__doc__ and attr.__doc__.startswith('+'):
            for c in (c for base in cls.__bases__ for c in base.mro()):
                doc = getattr(getattr(c, name), '__doc__')
                if doc:
                    attr.__doc__ = _append_doc(doc, attr.__doc__)
                    break

    return cls


class Policy(_PolicyBase, metaclass=abc.ABCMeta):
    raise_on_defect = False
    linesep = '\n'
    cte_type = '8bit'
    max_line_length = 78
    mangle_from_ = False
    message_factory = None

    def handle_defect(self, obj, defect):
        if self.raise_on_defect:
            raise defect
        self.register_defect(obj, defect)

    def register_defect(self, obj, defect):
        obj.defects.append(defect)

    def header_max_count(self, name):
        pass

    @abc.abstractmethod
    def header_source_parse(self, sourcelines):
        raise NotImplementedError

    @abc.abstractmethod
    def header_store_parse(self, name, value):
        raise NotImplementedError

    @abc.abstractmethod
    def header_fetch_parse(self, name, value):
        raise NotImplementedError

    @abc.abstractmethod
    def fold(self, name, value):
        raise NotImplementedError

    @abc.abstractmethod
    def fold_binary(self, name, value):
        raise NotImplementedError


@_extend_docstrings
class Compat32(Policy):
    mangle_from_ = True

    def _sanitize_header(self, name, value):
        if not isinstance(value, str):
            return value
        if _has_surrogates(value):
            return header.Header(value, charset=(_charset.UNKNOWN8BIT), header_name=name)
        return value

    def header_source_parse(self, sourcelines):
        name, value = sourcelines[0].split(':', 1)
        value = value.lstrip(' \t') + ''.join(sourcelines[1:])
        return (name, value.rstrip('\r\n'))

    def header_store_parse(self, name, value):
        return (
         name, value)

    def header_fetch_parse(self, name, value):
        return self._sanitize_header(name, value)

    def fold(self, name, value):
        return self._fold(name, value, sanitize=True)

    def fold_binary(self, name, value):
        folded = self._fold(name, value, sanitize=(self.cte_type == '7bit'))
        return folded.encode('ascii', 'surrogateescape')

    def _fold(self, name, value, sanitize):
        parts = []
        parts.append('%s: ' % name)
        if isinstance(value, str):
            if _has_surrogates(value):
                if sanitize:
                    h = header.Header(value, charset=(_charset.UNKNOWN8BIT),
                      header_name=name)
                else:
                    parts.append(value)
                    h = None
            else:
                h = header.Header(value, header_name=name)
        else:
            h = value
        if h is not None:
            maxlinelen = 0
            if self.max_line_length is not None:
                maxlinelen = self.max_line_length
            parts.append(h.encode(linesep=(self.linesep), maxlinelen=maxlinelen))
        parts.append(self.linesep)
        return ''.join(parts)


compat32 = Compat32()