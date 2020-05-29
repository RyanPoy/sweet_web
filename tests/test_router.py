#coding: utf8
from sweet_web.controller import Controller
from sweet_web.router import Router, Route
from collections import OrderedDict as oDict
from sanic.exceptions import NotFound
import unittest


class FooController(Controller):
        
    def foo_action(self):
        pass

class FakeController(object):
    def foo_actoin(self):
        pass


class TestRouter(unittest.TestCase):

    def setUp(self):
        self.router = Router()

    def test_should_give_me_error_when_handler_not_controller_subclass(self):
        with self.assertRaises(Exception) as err:
            Route("/save/<i:age>", 'get', FakeController, 'foo_action')
        self.assertEqual("'FakeController' does not a Controller class", str(err.exception))

    def test_dynamic_int(self):
        r = Route("/save/<i:age>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/(\\d+)/$", r.reg_uri)
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual(oDict({'age': int}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<i:age>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/(\\d+)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'age': int}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_float(self):
        r = Route("/floatAction/<f:value>", 'get', FooController, 'foo_action')
        self.assertEqual("^/floatAction/(\\d+(?:\\.\\d+)?)/$", r.reg_uri)
        self.assertEqual(oDict({'value': float}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/floatAction/<f:value>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/floatAction/(\\d+(?:\\.\\d+)?)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'value': float}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_str(self):
        r = Route("/save/<s:name>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<s:name>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_path(self):
        r = Route("/save/<p:name>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/(.+)/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<p:name>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/(.+)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_default(self):
        r = Route("/save/<name>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<name>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_default2(self):
        r = Route("/save/<:name>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<:name>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'name': str}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_dynamic_list(self):
        r = Route("/save/<a:ids>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/|^,]*(?:,[^/]*))/$", r.reg_uri)
        self.assertEqual(oDict({'ids': list}), r.name_and_type)
        self.assertEqual(False, r.is_static())

        r = Route("/save/<a:ids>/suffix", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/|^,]*(?:,[^/]*))/suffix/$", r.reg_uri)
        self.assertEqual(oDict({'ids': list}), r.name_and_type)
        self.assertEqual(False, r.is_static())

    def test_complex(self):
        r = Route("/save/<name>/<i:age>/<a:categories>", 'get', FooController, 'foo_action')
        self.assertEqual("^/save/([^/]+)/(\\d+)/([^/|^,]*(?:,[^/]*))/$", r.reg_uri)
        self.assertEqual(oDict({'name': str, 'age': int, 'categories': list}), r.name_and_type)
        self.assertEqual(False, r.is_static())
    
    def test_static_match(self):
        self.router.add("/hello/world", ['GET'], FooController, 'foo_action')
        r, param_dict = self.router.match('/hello/world', 'GET')
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual({}, param_dict)
        self.assertEqual(True, r.is_static())

    def test_static_with_multi_methods_match(self):
        self.router.add("/hello/world", ['GET', 'post'], FooController, 'foo_action')
        r, param_dict = self.router.match('/hello/world', 'GET')
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual({}, param_dict)
        self.assertEqual(True, r.is_static())

        r, param_dict = self.router.match('/hello/world', 'POST')
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual({}, param_dict)
        self.assertEqual(True, r.is_static())

    def test_dynamic_default_match(self):
        self.router.add('/hello/<name>', ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match('/hello/jon', 'get')
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual({'name': 'jon'}, param_dict)
        self.assertEqual(False, r.is_static())

        self.router.add('/hello/<:name>', ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match('/hello/jon', 'get')
        self.assertEqual(FooController, r.controller)
        self.assertEqual('foo_action', r.action)
        self.assertEqual({'name': 'jon'}, param_dict)
        self.assertEqual(False, r.is_static())

    def test_complex_match(self):
        self.router.add("/save/<name>/<i:age>/<a:categories>", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/save/pengyi/29/a,b,c,d,e", 'get')
        self.assertEqual("pengyi", param_dict['name'])
        self.assertEqual(29, param_dict['age'])
        self.assertEqual(['a','b','c','d','e'], param_dict['categories'])

        self.router.add("/save/<name>/<i:age>/<a:categories>/suffix", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/save/测试帐号/29/a,b,c,d,e/suffix", 'get')
        self.assertEqual("测试帐号", param_dict['name'])
        self.assertEqual(29, param_dict['age'])
        self.assertEqual(['a','b','c','d','e'], param_dict['categories'])

    def test_mgtv_se_match(self):
        self.router.add("/so/k-<name>", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/so/k-花儿与少年/", 'get')
        self.assertEqual("花儿与少年", param_dict['name'])

        r, param_dict = self.router.match("/so/k-花儿+少年/", 'get')
        self.assertEqual("花儿+少年", param_dict['name'])

    def test_mgtv_se_match2(self):
        self.router.add("/so/k-<p:name>", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/so/k-花儿+少年/再来一个", 'get')
        self.assertEqual("花儿+少年/再来一个", param_dict['name'])

    def test_mgtv_se_not_match(self):
        self.router.add("/so/k-<name>", ['get'], FooController, 'foo_action')
        with self.assertRaises(NotFound) as err:
            r, param_dict = self.router.match("/so/k-花/儿+少年/", 'get')

    def test_mgtv_list_match(self):
        self.router.add("/<i:category>/<idStr>.html", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/3/47-1----0-1----1---.html", 'get')
        self.assertEqual(3, param_dict['category'])
        self.assertEqual("47-1----0-1----1---", param_dict['idStr'])

    def test_float_match(self):
        self.router.add("/floatAction/<f:value>", ['get'], FooController, 'foo_action')
        r, param_dict = self.router.match("/floatAction/29.91", 'get')
        self.assertEqual(29.91, param_dict['value'])

    def test_channel_list_match(self):
        self.router.add(
            "/dynamic/v1/channel/list/<deviceId>/<mgtvVersion>/<osVersion>/<support>/<ticket>/<i:abroad>/<i:type>",
            ['GET'], FooController, 'foo_action'
        )
        r, param_dict = self.router.match("/dynamic/v1/channel/list/12345abc/6.5.1/10.3.3/1000000/12345qqwe/0/5", 'get')
        self.assertEqual("12345abc", param_dict['deviceId'])
        self.assertEqual("6.5.1", param_dict['mgtvVersion'])
        self.assertEqual("10.3.3", param_dict['osVersion'])
        self.assertEqual("1000000", param_dict['support'])
        self.assertEqual("12345qqwe", param_dict['ticket'])
        self.assertEqual(0, param_dict["abroad"])
        self.assertEqual(5, param_dict["type"])


if __name__ == '__main__':
    unitest.main()
