from cube import gl

import cubeapp.game
from cubeapp.game.event import Channel, Event
from cubeapp.game.entity.component import Transform, Component, Bindable, Drawable, Controller
from cubeapp.game.entity.system import System

class PlayerController(System):

    def __init__(self, event_manager, inputs):
        super().__init__()
        self.event_manager = event_manager
        self.inputs = inputs
        self.entity = None

    def init_component(self, entity, component):
        assert entity is not None
        assert self.entity is None
        kb = self.inputs.keyboard
        self.bind(
            (kb.up.key_held, component.move_up),
            (kb.down.key_held,  component.move_down),
            (kb.left.key_held,  component.move_left),
            (kb.right.key_held, component.move_right),
        )
        self.entity = entity
        self.channels = [
            component.move_up,
            component.move_down,
            component.move_left,
            component.move_right,
        ]
        self.event_manager.add(self)

    def bind(self, *items):
        for slot, chan in items:
            self.bind_one(slot, chan)

    def bind_one(self, slot, chan):
        slot.connect(
            lambda _: self.event_manager.push(Event(chan))
        )

    def __call__(self, ev, elapsed):
        print(ev, elapsed)
        self.entity.component('position').node.translate(ev.channel.dir)
        self.entity.component('light').content.point.position += ev.channel.dir

class PlayerBindings(Component):
    systems = [PlayerController]

    def __init__(self):
        self.move_left = Channel('left', dir = gl.vec3f(-1, 0, 0))
        self.move_right = Channel('right', dir = gl.vec3f(1, 0, 0))
        self.move_up = Channel('up', dir = gl.vec3f(0, 0, -1))
        self.move_down = Channel('down', dir = gl.vec3f(0, 0, 1))

def create(game):
    mat = gl.Material('player')
    def rand_color():
        import random
        return gl.col3f(random.random(), random.random(), random.random())
    mat.ambient = rand_color() #gl.col3f(0.2, 0.2, 0.2)
    #mat.diffuse = gl.col3f('black')
    #mat.specular = gl.col3f('black')
    mat.opacity = .5
    mesh = gl.Spheref(gl.vec3f(0), 1).drawable(game.renderer)
    light = game.renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0, 2, -1),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    game.entity_manager.add_system(PlayerController(game.event_manager, game.input_translator))

    player = game.entity_manager.create('player')
    player.add_component(
        Transform(
            gl.matrix.translate(gl.mat4f(), gl.vec3f(0, .9, 0)),
            name = 'position'
        ),
    )
    player.add_component(Bindable(light, name = 'light'))
    player.add_component(Bindable(mat, name = 'material'))
    player.add_component(Drawable(mesh))
    player.add_component(PlayerBindings())
    class ChangeColors:
        channels = ['tick']
        def __call__(self, ev, delta):
            import random
            mat.ambiant = rand_color()
    player.add_component(Controller(ChangeColors()))
    return player
