#coding: utf8
from sweet_web.router import Router, Route
from inspect import isawaitable
from queue import Queue as Q
from sanic import Sanic
import functools


class Application(object):

    router = Router()

    def __init__(self, router=None):
        cls = self.__class__
        self.app = Sanic('sweet-web')
        self.app.add_route(self.dispatch, '/', methods=Route.HTTP_METHODS)
        self.app.add_route(self.dispatch, '/<furi:path>', methods=Route.HTTP_METHODS)
        if router:
            self.static_routes = {}
            self.dynamic_routes = {}
            for r in router.all_routes():
                cls.router.add_route(r)

    def run(self, host='0.0.0.0', port=3000, debug=True, workers=3, 
            backlog=100, stop_event=None, register_sys_signals=True,
            access_log=None, **kwargs):

        print ('Run mode at %s:%s' % (host, port))

        self.app.run(host=host, port=port, debug=debug, workers=workers, backlog=backlog,
            stop_event=stop_event, register_sys_signals=register_sys_signals,
            access_log=access_log, auto_reload=debug, **kwargs)

    async def dispatch(self, request, furi=None):

        http_method = request.method.upper()
        uri = str(request.raw_url, encoding="utf-8")
        route, param_dict = self.router.match(uri, http_method)
        controller_object = route.controller(request)
        method = getattr(controller_object, route.action)

        response = method(**param_dict)
        if isawaitable(response):
            response = await response
        return response



############## http decorator ##############
class RoutesQ(Q):
    def get(self, block=True, timeout=None):
        if self.qsize() <= 0:
            return None
        return super().get(block=block, timeout=timeout)
routes_q = RoutesQ()


def get(uri):
    return route(uri, methods=['GET'])

def post(uri):
    return route(uri, methods=['POST'])

def put(uri):
    return route(uri, methods=['PUT'])

def head(uri):
    return route(uri, methods=['HEAD'])

def options(uri):
    return route(uri, methods=['OPTIONS'])

def patch(uri):
    return route(uri, methods=['PATCH'])

def delete(uri):
    return route(uri, methods=['DELETE'])

def route(uri, methods=None):
    methods = methods or ['GET']

    def wrapper(func):
        @functools.wraps(func)
        def _(*args, **kwargs):
            return func(*args, **kwargs)
        routes_q.put(dict(uri=uri, methods=methods, controller=None, action=func.__name__))
        return _
    return wrapper

