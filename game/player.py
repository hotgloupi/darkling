from cube import gl

import cubeapp.game
from cubeapp.game.event import Channel, Event
from cubeapp.game.entity.component import Controllers, Transform, View
from cubeapp.game.entity import Controller

class PlayerController(Controller):

    def __init__(self, entity):
        self.move_left = Channel('left', dir = gl.vec3f(-1, 0, 0))
        self.move_right = Channel('right', dir = gl.vec3f(1, 0, 0))
        self.move_up = Channel('up', dir = gl.vec3f(0, 0, -1))
        self.move_down = Channel('down', dir = gl.vec3f(0, 0, 1))
        super().__init__(entity,
            self.move_left,
            self.move_right,
            self.move_up,
            self.move_down,
        )
        kb = self.inputs.keyboard
        self.bind(
            (kb.up.key_held, self.move_up),
            (kb.down.key_held, self.move_down),
            (kb.left.key_held, self.move_left),
            (kb.right.key_held, self.move_right),
        )

    def bind(self, *items):
        for slot, chan in items:
            self.bind_one(slot, chan)

    def bind_one(self, slot, chan):
        slot.connect(
            lambda _: self.event_manager.push(Event(chan))
        )

    def fire(self, ev, elapsed):
        print(ev, elapsed)
        self.entity.component('transform').node.translate(ev.channel.dir)
        self.entity.component('view').nodes[0][1].point.position += ev.channel.dir

def create(game):
    mat = gl.Material('player')
    mat.ambient = gl.col3f('pink')
    mat.diffuse = gl.col3f('white')
    mat.specular = gl.col3f('white')
    mat.opacity = .5
    mesh = gl.Spheref(gl.vec3f(0), 1).drawable(game.renderer)
    light = game.renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0, 2, -1),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    return game.entity_manager.add(
        'player',
        Controllers,
        Transform,
        (View, {'parent_node': 'transform.node'}),
        view = {
            'contents': (light, mat, mesh),
        },
        transform = {
            'transformation': gl.matrix.translate(gl.mat4f(), gl.vec3f(0, .9, 0))
        },
        controllers = {
            'controllers': [PlayerController, ]
        },
    )

