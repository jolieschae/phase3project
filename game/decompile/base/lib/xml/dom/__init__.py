# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\dom\__init__.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 4159 bytes


class Node:
    __slots__ = ()
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11
    NOTATION_NODE = 12


INDEX_SIZE_ERR = 1
DOMSTRING_SIZE_ERR = 2
HIERARCHY_REQUEST_ERR = 3
WRONG_DOCUMENT_ERR = 4
INVALID_CHARACTER_ERR = 5
NO_DATA_ALLOWED_ERR = 6
NO_MODIFICATION_ALLOWED_ERR = 7
NOT_FOUND_ERR = 8
NOT_SUPPORTED_ERR = 9
INUSE_ATTRIBUTE_ERR = 10
INVALID_STATE_ERR = 11
SYNTAX_ERR = 12
INVALID_MODIFICATION_ERR = 13
NAMESPACE_ERR = 14
INVALID_ACCESS_ERR = 15
VALIDATION_ERR = 16

class DOMException(Exception):

    def __init__(self, *args, **kw):
        if self.__class__ is DOMException:
            raise RuntimeError('DOMException should not be instantiated directly')
        (Exception.__init__)(self, *args, **kw)

    def _get_code(self):
        return self.code


class IndexSizeErr(DOMException):
    code = INDEX_SIZE_ERR


class DomstringSizeErr(DOMException):
    code = DOMSTRING_SIZE_ERR


class HierarchyRequestErr(DOMException):
    code = HIERARCHY_REQUEST_ERR


class WrongDocumentErr(DOMException):
    code = WRONG_DOCUMENT_ERR


class InvalidCharacterErr(DOMException):
    code = INVALID_CHARACTER_ERR


class NoDataAllowedErr(DOMException):
    code = NO_DATA_ALLOWED_ERR


class NoModificationAllowedErr(DOMException):
    code = NO_MODIFICATION_ALLOWED_ERR


class NotFoundErr(DOMException):
    code = NOT_FOUND_ERR


class NotSupportedErr(DOMException):
    code = NOT_SUPPORTED_ERR


class InuseAttributeErr(DOMException):
    code = INUSE_ATTRIBUTE_ERR


class InvalidStateErr(DOMException):
    code = INVALID_STATE_ERR


class SyntaxErr(DOMException):
    code = SYNTAX_ERR


class InvalidModificationErr(DOMException):
    code = INVALID_MODIFICATION_ERR


class NamespaceErr(DOMException):
    code = NAMESPACE_ERR


class InvalidAccessErr(DOMException):
    code = INVALID_ACCESS_ERR


class ValidationErr(DOMException):
    code = VALIDATION_ERR


class UserDataHandler:
    NODE_CLONED = 1
    NODE_IMPORTED = 2
    NODE_DELETED = 3
    NODE_RENAMED = 4


XML_NAMESPACE = 'http://www.w3.org/XML/1998/namespace'
XMLNS_NAMESPACE = 'http://www.w3.org/2000/xmlns/'
XHTML_NAMESPACE = 'http://www.w3.org/1999/xhtml'
EMPTY_NAMESPACE = None
EMPTY_PREFIX = None
from .domreg import getDOMImplementation, registerDOMImplementation