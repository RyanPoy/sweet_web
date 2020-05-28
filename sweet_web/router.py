#coding: utf8
from collections import namedtuple, OrderedDict as oDict
from sanic.exceptions import MethodNotSupported, NotFound
from sweet_web.controller import Controller
import re

add_slash = lambda uri: uri if uri.endswith('/') else '%s/' % uri


class Route(object):

    class DefineError(Exception):
        pass

    HTTP_METHODS = set(['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
    URI_P = re.compile("<([a-zA-Z_][a-zA-Z_0-9]*)?(:[^>]*)?>")
    ARG_P = re.compile("^<(i:|f:|s:|a:|r:|p:|:)?([^>]*)>$")

    RE_MAPPING = {
        'i:': (int, r'(\d+)'),
        'f:': (float, r'(\d+(?:\.\d+)?)'),
        's:': (str, r'([^/]+)'),
        'p:': (str, r'(.+)'),
        'a:': (list, r'([^/|^,]*(?:,[^/]*))')
    }

    def __init__(self, uri, method, controller, action):
        uri = add_slash(uri)
        self.uri = uri
        self.method = self._init_method(method)
        self.controller = self.check_controller(controller)
        self.action = action
        self.reg_uri = None
        self.slash_count = uri.count('/')
        self.pattern = None
        self.name_and_type = oDict()
        self._init_reg_uri()

    def _init_method(self, method):
        method = method.upper()
        if method not in self.HTTP_METHODS:
            raise self.DefineError("Can not support http method[%s]" % method)
        return method

    def check_controller(self, controller):
        if issubclass(controller, Controller):
            return controller
        raise Exception("'%s' does not a Controller class" % controller.__name__)

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

    def match(self, uri, method=None):
        """ return matched, param_dict
        """
        uri = add_slash(uri)
        if method:
            method = method.upper()
        name_value_dict = oDict()
        if self.is_static():
            if self.uri != uri:
                return False, {}
            elif method and method != self.method:
                raise MethodNotSupported(
                    message="Method {} not allowed for URL {}".format(method, uri),
                    method=method,
                    allowed_methods=[self.method]
                )
            return True, name_value_dict

        else:
            m = self.pattern.match(uri)
            if not m:
                return False, name_value_dict
            elif method and method != self.method:
                raise MethodNotSupported(
                    message="Method {} not allowed for URL {}".format(method, uri),
                    method=method,
                    allowed_methods=[self.method]
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

    # Shorthand method decorators
    def get(self, uri, controller, action):
        return self.add(uri, methods=['GET'], controller=controller, action=action)

    def post(self, uri, controller, action):
        return self.add(uri, methods=['POST'], controller=controller, action=action)

    def put(self, uri, controller, action):
        return self.add(uri, methods=['PUT'], controller=controller, action=action)

    def head(self, uri, controller, action):
        return self.add(uri, methods=['HEAD'], controller=controller, action=action)

    def options(self, uri, controller, action):
        return self.add(uri, methods=['OPTIONS'], controller=controller, action=action)

    def patch(self, uri, controller, action):
        return self.add(uri, methods=['PATCH'], controller=controller, action=action)

    def delete(self, uri, controller, action):
        return self.add(uri, methods=['DELETE'], controller=controller, action=action)

    def trace(self, uri, controller, action):
        return self.add(uri, methods=['TRACE'], controller=controller, action=action)

    def add(self, uri, methods, controller, action):
        uri = add_slash(uri)
        for m in set(methods):
            r = Route(uri=uri, method=m, controller=controller, action=action)
            if r.is_static():
                self.static_routes.setdefault(uri, {}).setdefault(r.method, r)
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
        method_route_dict = self.static_routes.get(uri, None)
        if not method_route_dict:
            return None, {}
        elif method not in method_route_dict:
            raise MethodNotSupported(
                message="Method {} not allowed for URL {}".format(method, uri),
                method=method,
                allowed_methods=list(method_route_dict.keys())
            )
        return method_route_dict[method], {}

    def _dynamic_match(self, uri, method):
        slash_count = uri.count('/')
        if slash_count > self.max_slash_count:
            for rs in self.dynamic_routes.values():
                for r in rs:
                    is_match, param_dict = r.match(uri, None)
                    if is_match:
                        return r, param_dict
            return None, {}
        else:
            for cnt in self.dynamic_routes.keys():
                if cnt < slash_count:
                    continue
                for r in self.dynamic_routes.get(cnt):
                    is_match, param_dict = r.match(uri, None)
                    if is_match and r.method == method.upper():
                        return r, param_dict
            return None, {}
