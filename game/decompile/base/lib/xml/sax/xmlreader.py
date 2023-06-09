# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xml\sax\xmlreader.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 13064 bytes
from . import handler
from ._exceptions import SAXNotSupportedException, SAXNotRecognizedException

class XMLReader:

    def __init__(self):
        self._cont_handler = handler.ContentHandler()
        self._dtd_handler = handler.DTDHandler()
        self._ent_handler = handler.EntityResolver()
        self._err_handler = handler.ErrorHandler()

    def parse(self, source):
        raise NotImplementedError('This method must be implemented!')

    def getContentHandler(self):
        return self._cont_handler

    def setContentHandler(self, handler):
        self._cont_handler = handler

    def getDTDHandler(self):
        return self._dtd_handler

    def setDTDHandler(self, handler):
        self._dtd_handler = handler

    def getEntityResolver(self):
        return self._ent_handler

    def setEntityResolver(self, resolver):
        self._ent_handler = resolver

    def getErrorHandler(self):
        return self._err_handler

    def setErrorHandler(self, handler):
        self._err_handler = handler

    def setLocale(self, locale):
        raise SAXNotSupportedException('Locale support not implemented')

    def getFeature(self, name):
        raise SAXNotRecognizedException("Feature '%s' not recognized" % name)

    def setFeature(self, name, state):
        raise SAXNotRecognizedException("Feature '%s' not recognized" % name)

    def getProperty(self, name):
        raise SAXNotRecognizedException("Property '%s' not recognized" % name)

    def setProperty(self, name, value):
        raise SAXNotRecognizedException("Property '%s' not recognized" % name)


class IncrementalParser(XMLReader):

    def __init__(self, bufsize=65536):
        self._bufsize = bufsize
        XMLReader.__init__(self)

    def parse(self, source):
        from . import saxutils
        source = saxutils.prepare_input_source(source)
        self.prepareParser(source)
        file = source.getCharacterStream()
        if file is None:
            file = source.getByteStream()
        buffer = file.read(self._bufsize)
        while buffer:
            self.feed(buffer)
            buffer = file.read(self._bufsize)

        self.close()

    def feed(self, data):
        raise NotImplementedError('This method must be implemented!')

    def prepareParser(self, source):
        raise NotImplementedError('prepareParser must be overridden!')

    def close(self):
        raise NotImplementedError('This method must be implemented!')

    def reset(self):
        raise NotImplementedError('This method must be implemented!')


class Locator:

    def getColumnNumber(self):
        return -1

    def getLineNumber(self):
        return -1

    def getPublicId(self):
        pass

    def getSystemId(self):
        pass


class InputSource:

    def __init__(self, system_id=None):
        self._InputSource__system_id = system_id
        self._InputSource__public_id = None
        self._InputSource__encoding = None
        self._InputSource__bytefile = None
        self._InputSource__charfile = None

    def setPublicId(self, public_id):
        self._InputSource__public_id = public_id

    def getPublicId(self):
        return self._InputSource__public_id

    def setSystemId(self, system_id):
        self._InputSource__system_id = system_id

    def getSystemId(self):
        return self._InputSource__system_id

    def setEncoding(self, encoding):
        self._InputSource__encoding = encoding

    def getEncoding(self):
        return self._InputSource__encoding

    def setByteStream(self, bytefile):
        self._InputSource__bytefile = bytefile

    def getByteStream(self):
        return self._InputSource__bytefile

    def setCharacterStream(self, charfile):
        self._InputSource__charfile = charfile

    def getCharacterStream(self):
        return self._InputSource__charfile


class AttributesImpl:

    def __init__(self, attrs):
        self._attrs = attrs

    def getLength(self):
        return len(self._attrs)

    def getType(self, name):
        return 'CDATA'

    def getValue(self, name):
        return self._attrs[name]

    def getValueByQName(self, name):
        return self._attrs[name]

    def getNameByQName(self, name):
        if name not in self._attrs:
            raise KeyError(name)
        return name

    def getQNameByName(self, name):
        if name not in self._attrs:
            raise KeyError(name)
        return name

    def getNames(self):
        return list(self._attrs.keys())

    def getQNames(self):
        return list(self._attrs.keys())

    def __len__(self):
        return len(self._attrs)

    def __getitem__(self, name):
        return self._attrs[name]

    def keys(self):
        return list(self._attrs.keys())

    def __contains__(self, name):
        return name in self._attrs

    def get(self, name, alternative=None):
        return self._attrs.get(name, alternative)

    def copy(self):
        return self.__class__(self._attrs)

    def items(self):
        return list(self._attrs.items())

    def values(self):
        return list(self._attrs.values())


class AttributesNSImpl(AttributesImpl):

    def __init__(self, attrs, qnames):
        self._attrs = attrs
        self._qnames = qnames

    def getValueByQName(self, name):
        for nsname, qname in self._qnames.items():
            if qname == name:
                return self._attrs[nsname]

        raise KeyError(name)

    def getNameByQName(self, name):
        for nsname, qname in self._qnames.items():
            if qname == name:
                return nsname

        raise KeyError(name)

    def getQNameByName(self, name):
        return self._qnames[name]

    def getQNames(self):
        return list(self._qnames.values())

    def copy(self):
        return self.__class__(self._attrs, self._qnames)


def _test():
    XMLReader()
    IncrementalParser()
    Locator()


if __name__ == '__main__':
    _test()