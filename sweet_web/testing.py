#coding: utf8
from sweet_web.application import Application
from demo_server import router
import unittest
import sanic
sanic.log.LOGGING_CONFIG_DEFAULTS['loggers']['sanic.root']['level'] = 'WARNING'
sanic.log.LOGGING_CONFIG_DEFAULTS['loggers']['sanic.access']['level'] = 'WARNING'


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.application = Application(router=router)
    
    @property
    def client(self):
        return self.application.app.test_client

    def get(self, *args, **kwargs):
        return self.client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        return self.client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.client.delete(*args, **kwargs)

    def patch(self, *args, **kwargs):
        return self.client.patch(*args, **kwargs)

    def options(self, *args, **kwargs):
        return self.client.options(*args, **kwargs)

    def head(self, *args, **kwargs):
        return self.client.head(*args, **kwargs)

    def websocket(self, *args, **kwargs):
        return self.client.websocket(*args, **kwargs)
