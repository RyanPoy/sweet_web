#coding: utf8
from sweet_web.application import *
from sweet_web.controller import Controller
from sweet_web.router import Router


class UserController(Controller):
    
    @get('/hello')
    async def hello(self):
        return self.render_str('UserController#Hello')

    @get('/hello2/<name>')
    async def hello2(self, name):
        return self.render_str('UserController#Hello2: %s[%s]' % (name, type(name)))

    async def list(self):
        return self.render_str('UserController#list')

    def show(self, id):
        return self.render_str('UserController#show:%s[%s]' % (id, type(id)))

    def create(self):
        return self.render_str('UserController#create')

    def new(self):
        return self.render_str('UserController#new')

    def delete(self, id):
        print ("delete")
        return self.render_str('UserController#delete:%s[%s]' % (id, type(id)))

    def update(self, id):
        print ("update")
        return self.render_str('UserController#update:%s[%s]' % (id, type(id)))


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
