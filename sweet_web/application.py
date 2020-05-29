#coding: utf8
import logging
from sanic import Sanic
from sweet_web.router import Router, Route
from sanic.views import HTTPMethodView
from inspect import isawaitable
import functools
from sanic.response import text, json


class Application(object):

    def __init__(self, router):
        self.app = Sanic('sweet-web')
        self.app.add_route(self.dispatch, '/', methods=Route.HTTP_METHODS)
        self.app.add_route(self.dispatch, '/<furi:path>', methods=Route.HTTP_METHODS)
        self.router = router

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
