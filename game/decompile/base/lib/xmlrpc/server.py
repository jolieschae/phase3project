# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.7.16 (default, May 16 2023, 11:05:37) 
# [Clang 13.0.0 (clang-1300.0.29.30)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Lib\xmlrpc\server.py
# Compiled at: 2018-06-26 23:07:36
# Size of source mod 2**32: 38357 bytes
from xmlrpc.client import Fault, dumps, loads, gzip_encode, gzip_decode
from http.server import BaseHTTPRequestHandler
from functools import partial
import http.server, socketserver, sys, os, re, pydoc, inspect, traceback
try:
    import fcntl
except ImportError:
    fcntl = None

def resolve_dotted_attribute(obj, attr, allow_dotted_names=True):
    if allow_dotted_names:
        attrs = attr.split('.')
    else:
        attrs = [
         attr]
    for i in attrs:
        if i.startswith('_'):
            raise AttributeError('attempt to access private attribute "%s"' % i)
        else:
            obj = getattr(obj, i)

    return obj


def list_public_methods(obj):
    return [member for member in dir(obj) if not member.startswith('_') if callable(getattr(obj, member))]


class SimpleXMLRPCDispatcher:

    def __init__(self, allow_none=False, encoding=None, use_builtin_types=False):
        self.funcs = {}
        self.instance = None
        self.allow_none = allow_none
        self.encoding = encoding or 'utf-8'
        self.use_builtin_types = use_builtin_types

    def register_instance(self, instance, allow_dotted_names=False):
        self.instance = instance
        self.allow_dotted_names = allow_dotted_names

    def register_function(self, function=None, name=None):
        if function is None:
            return partial((self.register_function), name=name)
        if name is None:
            name = function.__name__
        self.funcs[name] = function
        return function

    def register_introspection_functions(self):
        self.funcs.update({'system.listMethods':self.system_listMethods,  'system.methodSignature':self.system_methodSignature, 
         'system.methodHelp':self.system_methodHelp})

    def register_multicall_functions(self):
        self.funcs.update({'system.multicall': self.system_multicall})

    def _marshaled_dispatch(self, data, dispatch_method=None, path=None):
        try:
            params, method = loads(data, use_builtin_types=(self.use_builtin_types))
            if dispatch_method is not None:
                response = dispatch_method(method, params)
            else:
                response = self._dispatch(method, params)
            response = (response,)
            response = dumps(response, methodresponse=1, allow_none=(self.allow_none),
              encoding=(self.encoding))
        except Fault as fault:
            try:
                response = dumps(fault, allow_none=(self.allow_none), encoding=(self.encoding))
            finally:
                fault = None
                del fault

        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            try:
                response = dumps((Fault(1, '%s:%s' % (exc_type, exc_value))),
                  encoding=(self.encoding),
                  allow_none=(self.allow_none))
            finally:
                exc_type = exc_value = exc_tb = None

        return response.encode(self.encoding, 'xmlcharrefreplace')

    def system_listMethods(self):
        methods = set(self.funcs.keys())
        if self.instance is not None:
            if hasattr(self.instance, '_listMethods'):
                methods |= set(self.instance._listMethods())
            else:
                if not hasattr(self.instance, '_dispatch'):
                    methods |= set(list_public_methods(self.instance))
        return sorted(methods)

    def system_methodSignature(self, method_name):
        return 'signatures not supported'

    def system_methodHelp(self, method_name):
        method = None
        if method_name in self.funcs:
            method = self.funcs[method_name]
        else:
            if self.instance is not None:
                if hasattr(self.instance, '_methodHelp'):
                    return self.instance._methodHelp(method_name)
                if not hasattr(self.instance, '_dispatch'):
                    try:
                        method = resolve_dotted_attribute(self.instance, method_name, self.allow_dotted_names)
                    except AttributeError:
                        pass

        if method is None:
            return ''
        return pydoc.getdoc(method)

    def system_multicall(self, call_list):
        results = []
        for call in call_list:
            method_name = call['methodName']
            params = call['params']
            try:
                results.append([self._dispatch(method_name, params)])
            except Fault as fault:
                try:
                    results.append({'faultCode':fault.faultCode, 
                     'faultString':fault.faultString})
                finally:
                    fault = None
                    del fault

            except:
                exc_type, exc_value, exc_tb = sys.exc_info()
                try:
                    results.append({'faultCode':1, 
                     'faultString':'%s:%s' % (exc_type, exc_value)})
                finally:
                    exc_type = exc_value = exc_tb = None

        return results

    def _dispatch(self, method, params):
        try:
            func = self.funcs[method]
        except KeyError:
            pass
        else:
            if func is not None:
                return func(*params)
                raise Exception('method "%s" is not supported' % method)
            elif self.instance is not None:
                if hasattr(self.instance, '_dispatch'):
                    return self.instance._dispatch(method, params)
                try:
                    func = resolve_dotted_attribute(self.instance, method, self.allow_dotted_names)
                except AttributeError:
                    pass

                if func is not None:
                    return func(*params)
            raise Exception('method "%s" is not supported' % method)


class SimpleXMLRPCRequestHandler(BaseHTTPRequestHandler):
    rpc_paths = ('/', '/RPC2')
    encode_threshold = 1400
    wbufsize = -1
    disable_nagle_algorithm = True
    aepattern = re.compile('\n                            \\s* ([^\\s;]+) \\s*            #content-coding\n                            (;\\s* q \\s*=\\s* ([0-9\\.]+))? #q\n                            ', re.VERBOSE | re.IGNORECASE)

    def accept_encodings(self):
        r = {}
        ae = self.headers.get('Accept-Encoding', '')
        for e in ae.split(','):
            match = self.aepattern.match(e)
            if match:
                v = match.group(3)
                v = float(v) if v else 1.0
                r[match.group(1)] = v

        return r

    def is_rpc_path_valid(self):
        if self.rpc_paths:
            return self.path in self.rpc_paths
        return True

    def do_POST(self):
        if not self.is_rpc_path_valid():
            self.report_404()
            return
        try:
            max_chunk_size = 10485760
            size_remaining = int(self.headers['content-length'])
            L = []
            while size_remaining:
                chunk_size = min(size_remaining, max_chunk_size)
                chunk = self.rfile.read(chunk_size)
                if not chunk:
                    break
                L.append(chunk)
                size_remaining -= len(L[-1])

            data = (b'').join(L)
            data = self.decode_request_content(data)
            if data is None:
                return
            response = self.server._marshaled_dispatch(data, getattr(self, '_dispatch', None), self.path)
        except Exception as e:
            try:
                self.send_response(500)
                if hasattr(self.server, '_send_traceback_header'):
                    if self.server._send_traceback_header:
                        self.send_header('X-exception', str(e))
                        trace = traceback.format_exc()
                        trace = str(trace.encode('ASCII', 'backslashreplace'), 'ASCII')
                        self.send_header('X-traceback', trace)
                self.send_header('Content-length', '0')
                self.end_headers()
            finally:
                e = None
                del e

        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            if self.encode_threshold is not None and len(response) > self.encode_threshold:
                q = self.accept_encodings().get('gzip', 0)
                if q:
                    try:
                        response = gzip_encode(response)
                        self.send_header('Content-Encoding', 'gzip')
                    except NotImplementedError:
                        pass

            self.send_header('Content-length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

    def decode_request_content(self, data):
        encoding = self.headers.get('content-encoding', 'identity').lower()
        if encoding == 'identity':
            return data
            if encoding == 'gzip':
                try:
                    return gzip_decode(data)
                except NotImplementedError:
                    self.send_response(501, 'encoding %r not supported' % encoding)
                except ValueError:
                    self.send_response(400, 'error decoding gzip content')

        else:
            self.send_response(501, 'encoding %r not supported' % encoding)
        self.send_header('Content-length', '0')
        self.end_headers()

    def report_404(self):
        self.send_response(404)
        response = b'No such page'
        self.send_header('Content-type', 'text/plain')
        self.send_header('Content-length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_request(self, code='-', size='-'):
        if self.server.logRequests:
            BaseHTTPRequestHandler.log_request(self, code, size)


class SimpleXMLRPCServer(socketserver.TCPServer, SimpleXMLRPCDispatcher):
    allow_reuse_address = True
    _send_traceback_header = False

    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler, logRequests=True, allow_none=False, encoding=None, bind_and_activate=True, use_builtin_types=False):
        self.logRequests = logRequests
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)
        socketserver.TCPServer.__init__(self, addr, requestHandler, bind_and_activate)


class MultiPathXMLRPCServer(SimpleXMLRPCServer):

    def __init__(self, addr, requestHandler=SimpleXMLRPCRequestHandler, logRequests=True, allow_none=False, encoding=None, bind_and_activate=True, use_builtin_types=False):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none, encoding, bind_and_activate, use_builtin_types)
        self.dispatchers = {}
        self.allow_none = allow_none
        self.encoding = encoding or 'utf-8'

    def add_dispatcher(self, path, dispatcher):
        self.dispatchers[path] = dispatcher
        return dispatcher

    def get_dispatcher(self, path):
        return self.dispatchers[path]

    def _marshaled_dispatch(self, data, dispatch_method=None, path=None):
        try:
            response = self.dispatchers[path]._marshaled_dispatch(data, dispatch_method, path)
        except:
            exc_type, exc_value = sys.exc_info()[:2]
            try:
                response = dumps((Fault(1, '%s:%s' % (exc_type, exc_value))),
                  encoding=(self.encoding),
                  allow_none=(self.allow_none))
                response = response.encode(self.encoding, 'xmlcharrefreplace')
            finally:
                exc_type = exc_value = None

        return response


class CGIXMLRPCRequestHandler(SimpleXMLRPCDispatcher):

    def __init__(self, allow_none=False, encoding=None, use_builtin_types=False):
        SimpleXMLRPCDispatcher.__init__(self, allow_none, encoding, use_builtin_types)

    def handle_xmlrpc(self, request_text):
        response = self._marshaled_dispatch(request_text)
        print('Content-Type: text/xml')
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def handle_get(self):
        code = 400
        message, explain = BaseHTTPRequestHandler.responses[code]
        response = http.server.DEFAULT_ERROR_MESSAGE % {'code':code, 
         'message':message, 
         'explain':explain}
        response = response.encode('utf-8')
        print('Status: %d %s' % (code, message))
        print('Content-Type: %s' % http.server.DEFAULT_ERROR_CONTENT_TYPE)
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def handle_request(self, request_text=None):
        if request_text is None and os.environ.get('REQUEST_METHOD', None) == 'GET':
            self.handle_get()
        else:
            try:
                length = int(os.environ.get('CONTENT_LENGTH', None))
            except (ValueError, TypeError):
                length = -1

            if request_text is None:
                request_text = sys.stdin.read(length)
            self.handle_xmlrpc(request_text)


class ServerHTMLDoc(pydoc.HTMLDoc):

    def markup(self, text, escape=None, funcs={}, classes={}, methods={}):
        escape = escape or self.escape
        results = []
        here = 0
        pattern = re.compile('\\b((http|ftp)://\\S+[\\w/]|RFC[- ]?(\\d+)|PEP[- ]?(\\d+)|(self\\.)?((?:\\w|\\.)+))\\b')
        while True:
            match = pattern.search(text, here)
            if not match:
                break
            else:
                start, end = match.span()
                results.append(escape(text[here:start]))
                all, scheme, rfc, pep, selfdot, name = match.groups()
                if scheme:
                    url = escape(all).replace('"', '&quot;')
                    results.append('<a href="%s">%s</a>' % (url, url))
                else:
                    if rfc:
                        url = 'http://www.rfc-editor.org/rfc/rfc%d.txt' % int(rfc)
                        results.append('<a href="%s">%s</a>' % (url, escape(all)))
                    else:
                        if pep:
                            url = 'http://www.python.org/dev/peps/pep-%04d/' % int(pep)
                            results.append('<a href="%s">%s</a>' % (url, escape(all)))
                        else:
                            if text[end:end + 1] == '(':
                                results.append(self.namelink(name, methods, funcs, classes))
                            else:
                                if selfdot:
                                    results.append('self.<strong>%s</strong>' % name)
                                else:
                                    results.append(self.namelink(name, classes))
            here = end

        results.append(escape(text[here:]))
        return ''.join(results)

    def docroutine(self, object, name, mod=None, funcs={}, classes={}, methods={}, cl=None):
        anchor = (cl and cl.__name__ or '') + '-' + name
        note = ''
        title = '<a name="%s"><strong>%s</strong></a>' % (
         self.escape(anchor), self.escape(name))
        if inspect.ismethod(object):
            args = inspect.getfullargspec(object)
            argspec = inspect.formatargspec((args.args[1:]),
              (args.varargs),
              (args.varkw),
              (args.defaults),
              annotations=(args.annotations),
              formatvalue=(self.formatvalue))
        else:
            if inspect.isfunction(object):
                args = inspect.getfullargspec(object)
                argspec = inspect.formatargspec((args.args),
                  (args.varargs), (args.varkw), (args.defaults), annotations=(args.annotations),
                  formatvalue=(self.formatvalue))
            else:
                argspec = '(...)'
        if isinstance(object, tuple):
            argspec = object[0] or argspec
            docstring = object[1] or ''
        else:
            docstring = pydoc.getdoc(object)
        decl = title + argspec + (note and self.grey('<font face="helvetica, arial">%s</font>' % note))
        doc = self.markup(docstring, self.preformat, funcs, classes, methods)
        doc = doc and '<dd><tt>%s</tt></dd>' % doc
        return '<dl><dt>%s</dt>%s</dl>\n' % (decl, doc)

    def docserver(self, server_name, package_documentation, methods):
        fdict = {}
        for key, value in methods.items():
            fdict[key] = '#-' + key
            fdict[value] = fdict[key]

        server_name = self.escape(server_name)
        head = '<big><big><strong>%s</strong></big></big>' % server_name
        result = self.heading(head, '#ffffff', '#7799ee')
        doc = self.markup(package_documentation, self.preformat, fdict)
        doc = doc and '<tt>%s</tt>' % doc
        result = result + '<p>%s</p>\n' % doc
        contents = []
        method_items = sorted(methods.items())
        for key, value in method_items:
            contents.append(self.docroutine(value, key, funcs=fdict))

        result = result + self.bigsection('Methods', '#ffffff', '#eeaa77', ''.join(contents))
        return result


class XMLRPCDocGenerator:

    def __init__(self):
        self.server_name = 'XML-RPC Server Documentation'
        self.server_documentation = 'This server exports the following methods through the XML-RPC protocol.'
        self.server_title = 'XML-RPC Server Documentation'

    def set_server_title(self, server_title):
        self.server_title = server_title

    def set_server_name(self, server_name):
        self.server_name = server_name

    def set_server_documentation(self, server_documentation):
        self.server_documentation = server_documentation

    def generate_html_documentation(self):
        methods = {}
        for method_name in self.system_listMethods():
            if method_name in self.funcs:
                method = self.funcs[method_name]
            elif self.instance is not None:
                method_info = [
                 None, None]
                if hasattr(self.instance, '_get_method_argstring'):
                    method_info[0] = self.instance._get_method_argstring(method_name)
                if hasattr(self.instance, '_methodHelp'):
                    method_info[1] = self.instance._methodHelp(method_name)
                method_info = tuple(method_info)
                if method_info != (None, None):
                    method = method_info
                elif not hasattr(self.instance, '_dispatch'):
                    try:
                        method = resolve_dotted_attribute(self.instance, method_name)
                    except AttributeError:
                        method = method_info

                else:
                    method = method_info

        documenter = ServerHTMLDoc()
        documentation = documenter.docserver(self.server_name, self.server_documentation, methods)
        return documenter.page(self.server_title, documentation)


class DocXMLRPCRequestHandler(SimpleXMLRPCRequestHandler):

    def do_GET(self):
        if not self.is_rpc_path_valid():
            self.report_404()
            return
        response = self.server.generate_html_documentation().encode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)


class DocXMLRPCServer(SimpleXMLRPCServer, XMLRPCDocGenerator):

    def __init__(self, addr, requestHandler=DocXMLRPCRequestHandler, logRequests=True, allow_none=False, encoding=None, bind_and_activate=True, use_builtin_types=False):
        SimpleXMLRPCServer.__init__(self, addr, requestHandler, logRequests, allow_none, encoding, bind_and_activate, use_builtin_types)
        XMLRPCDocGenerator.__init__(self)


class DocCGIXMLRPCRequestHandler(CGIXMLRPCRequestHandler, XMLRPCDocGenerator):

    def handle_get(self):
        response = self.generate_html_documentation().encode('utf-8')
        print('Content-Type: text/html')
        print('Content-Length: %d' % len(response))
        print()
        sys.stdout.flush()
        sys.stdout.buffer.write(response)
        sys.stdout.buffer.flush()

    def __init__(self):
        CGIXMLRPCRequestHandler.__init__(self)
        XMLRPCDocGenerator.__init__(self)


if __name__ == '__main__':
    import datetime

    class ExampleService:

        def getData(self):
            return '42'

        class currentTime:

            @staticmethod
            def getCurrentTime():
                return datetime.datetime.now()


    with SimpleXMLRPCServer(('localhost', 8000)) as (server):
        server.register_function(pow)
        server.register_function(lambda x, y: x + y, 'add')
        server.register_instance((ExampleService()), allow_dotted_names=True)
        server.register_multicall_functions()
        print('Serving XML-RPC on localhost port 8000')
        print('It is advisable to run this example server within a secure, closed network.')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nKeyboard interrupt received, exiting.')
            sys.exit(0)