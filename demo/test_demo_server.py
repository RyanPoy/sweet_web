#coding: utf8
from sweet_web.testing import BaseTestCase
import unittest
import json


class TestDemoServer(BaseTestCase):

    def test_get_users_list(self):
        request, response = self.get('/users')
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#list', response.text)
    
    def test_get_users_show(self):
        request, response = self.get('/users/123')
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#show:123', response.text)

    def test_post_users_show(self):
        request, response = self.post('/users', data=json.dumps({
            'name': 'Jon',
            'age': 32,
        }))
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#create: User["Jon", 32]', response.text)

    def test_get_users_new(self):
        request, response = self.get('/users/new')
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#new', response.text)

    def test_delete_users_delete(self):
        request, response = self.delete('/users/123')
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#delete:123', response.text)

    def test_put_users_update(self):
        request, response = self.put('/users/123', data=json.dumps({
            'name': 'Jon',
            'age': 32,
        }))
        self.assertEqual(200, response.status_code)
        self.assertEqual('UserController#update: User[123, "Jon", 32]', response.text)

    def test_get_hello(self):
        request, response = self.get('/hello')
        self.assertEqual(200, response.status_code)
        self.assertEqual('HelloController#Hello', response.text)

    def test_get_hello2(self):
        request, response = self.get('/hello2/Jon')
        self.assertEqual(200, response.status_code)
        self.assertEqual('HelloController#Hello2: Jon', response.text)

    def test_get_hello3(self):
        request, response = self.get('/hello3/Jon')
        self.assertEqual(200, response.status_code)
        self.assertEqual('HelloController#Hello3: Jon', response.text)

    def test_post_hello3(self):
        request, response = self.post('/hello3/Jon')
        self.assertEqual(200, response.status_code)
        self.assertEqual('HelloController#Hello3: Jon', response.text)


if __name__ == '__main__':
    unittest.main()
