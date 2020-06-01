#coding: utf8
from sweet_web.application import *
from sweet_web.controller import Controller
from sweet_web.router import Router


class UserController(Controller):
    
    async def list(self):
        return self.render_str('UserController#list')

    def show(self, id):
        return self.render_str('UserController#show:%s' % id)

    def create(self):
        name = self.arg('name')
        age = self.int_arg('age')
        return self.render_str('UserController#create: User["%s", %s]' % (name, age))

    def new(self):
        return self.render_str('UserController#new')

    def delete(self, id):
        return self.render_str('UserController#delete:%s' % id)

    def update(self, id):
        name = self.arg('name')
        age = self.int_arg('age')
        return self.render_str('UserController#update: User[%s, "%s", %s]' % (id, name, age))


class HelloController(Controller):

    @get('/hello')
    async def hello(self):
        return self.render_str('HelloController#Hello')

    @get('/hello2/<name>')
    async def hello2(self, name):
        return self.render_str('HelloController#Hello2: %s' % name)

    @route('/hello3/<name>', methods=['GET', 'POST'])
    async def hello3(self, name):
        return self.render_str('HelloController#Hello3: %s' % name)


router = Router()
router.get('/users', UserController, 'list')
router.get('/users/<id>', UserController, 'show')
router.post('/users', UserController, 'create')
router.get('/users/new', UserController, 'new')
router.delete('/users/<id>', UserController, 'delete')
router.put('/users/<id>', UserController, 'update')


if __name__ == '__main__':
    app = Application(router=router)
    app.run(debug=True)
