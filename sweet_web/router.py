#coding: utf8
from collections import namedtuple, OrderedDict as oDict
from sanic.exceptions import MethodNotSupported, NotFound
import re

add_slash = lambda uri: uri if uri.endswith('/') else '%s/' % uri


class Route(object):

    class DefineError(Exception):
        pass

    HTTP_METHODS = set(['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE'])
    URI_P = re.compile("<([a-zA-Z_][a-zA-Z_0-9]*)?(:[^>]*)?>")
    ARG_P = re.compile("^<(i:|f:|s:|a:|r:|p:|:)?([^>]*)>$")

    RE_MAPPING = {
        'i:': (int, r'(\d+)'),
        'f:': (float, r'(\d+(?:\.\d+)?)'),
        's:': (str, r'([^/]+)'),
        'p:': (str, r'(.+)'),
        'a:': (list, r'([^/|^,]*(?:,[^/]*))')
    }

    def __init__(self, uri, methods, controller, action):
        uri = add_slash(uri)
        self.uri = uri
        self.methods = self._init_methods(methods)
        self.controller = controller
        self.action = action
        self.reg_uri = None
        self.slash_count = uri.count('/')
        self.pattern = None
        self.name_and_type = oDict()
        self._init_reg_uri()

    def _init_methods(self, methods):
        ms = set()
        for m in methods:
            m = m.upper()
            if m not in self.HTTP_METHODS:
                raise DefineError("Can not support http method[%s]" % m)
            ms.add(m)
        return ms

    def is_static(self):
        return self.reg_uri is None

    def _iter_of(self, uri):
        start = 0
        for m in self.URI_P.finditer(uri):
            matched = True
            begin, end = m.span()
            if begin > start:
                yield uri[start:begin]
            start = begin
            if begin < end:
                yield uri[begin:end]
            start = end
        if start < len(uri):
            yield uri[start:]

    def _init_reg_uri(self):
        uri, matched, buff = self.uri, False, []
        for item in self._iter_of(uri):
            m = self.ARG_P.match(item)
            if not m:
                buff.append(item)
                continue
            gs = m.groups()
            t = 's:' if gs[0] is None or gs[0] == ':' else gs[0]
            if t == 'r': # reg
                buff.append(item)
            elif t not in self.RE_MAPPING:
                raise self.DefineError('Can not support type[%s]' % t)
            else:
                type_and_restr = self.RE_MAPPING[t]
                buff.append(type_and_restr[1])
                self.name_and_type[gs[1]] = type_and_restr[0]
                # buff.append('(?P<{name}>{re_str})'.format(name=gs[1], re_str=re_str))
            matched = True
        if matched:
            self.reg_uri = '^'+''.join(buff)+'$'
            self.pattern = re.compile(self.reg_uri)


    def match(self, uri, method="GET"):
        """ return matched, param_dict
        """
        uri = add_slash(uri)
        method = method.upper()
        name_value_dict = oDict()
        if self.is_static():
            if self.uri != uri:
                return False, {}
            elif method not in self.methods:
                raise MethodNotSupported(
                    message="Method {} not allowed for URL {}".format(method, uri),
                    method=method,
                    allowed_methods=self.methods
                )
            return True, name_value_dict

        else:
            m = self.pattern.match(uri)
            if not m:
                return False, name_value_dict
            elif method not in self.methods:
                raise MethodNotSupported(
                    message="Method {} not allowed for URL {}".format(method, uri),
                    method=method,
                    allowed_methods=self.methods
                )
            else:
                names = list(self.name_and_type.keys())
                for idx, g in enumerate(m.groups()):
                    name = names[idx]
                    type_ = self.name_and_type[name]
                    if type_ == list:
                        value = [ x.strip() for x in g.split(',') if x and x.strip() ]
                    else:
                        value = type_(g)
                    name_value_dict[name] = value
                return True, name_value_dict


class Router(object):
    
    def __init__(self):
        self.static_routes = {}
        self.dynamic_routes = {}
        self.max_slash_count = 0

    def add(self, uri, methods, controller, action):
        uri = add_slash(uri)
        r = Route(uri=uri, methods=methods, controller=controller, action=action)

        if r.is_static():
            self.static_routes[uri] = r
        else:
            self.dynamic_routes.setdefault(r.slash_count, []).append(r)
            self.max_slash_count = max(self.dynamic_routes.keys())
        return self

    def match(self, uri, method):
        uri = add_slash(uri)
        method = method.upper()

        route, param_dict = self._static_match(uri, method)
        if not route:
            route, param_dict = self._dynamic_match(uri, method)
        if not route:
            raise NotFound("Requested URL {} not found".format(uri))
        return route, param_dict

    def _static_match(self, uri, method):
        route = self.static_routes.get(uri, None)
        if not route:
            return None, {}
        elif method not in route.methods:
            raise MethodNotSupported(
                message="Method {} not allowed for URL {}".format(method, uri),
                method=method,
                allowed_methods=route.methods
            )
        return route, {}

    def _dynamic_match(self, uri, method):
        slash_count = uri.count('/')
        if slash_count > self.max_slash_count:
            for rs in self.dynamic_routes.values():
                for r in rs:
                    is_match, param_dict = r.match(uri, method)
                    if is_match:
                        return r, param_dict
            return None, {}
        else:
            for cnt in self.dynamic_routes.keys():
                if cnt < slash_count:
                    continue
                for r in self.dynamic_routes.get(cnt):
                    is_match, param_dict = r.match(uri, method)
                    if is_match:
                        return r, param_dict
            return None, {}
