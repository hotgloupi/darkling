from cube import gl, gui, units
from cube.system.inputs import KeySym

from . import player
from . import ground
from . import darkling

import cubeapp.game
from cubeapp.game.entity.component import Controller
from cubeapp.game.event import Channel, Event

class CameraController:

    def __init__(self, cam):
        super().__init__()
        self.move_left =  Channel(dir = gl.vec3f(-1, 0, 0))
        self.move_right = Channel(dir = gl.vec3f(1, 0, 0))
        self.move_up =    Channel(dir = gl.vec3f(0, 0, -1))
        self.move_down =  Channel(dir = gl.vec3f(0, 0, 1))
        self.channels = [
            self.move_left,
            self.move_right,
            self.move_up,
            self.move_down,
        ]


    def __call__(self, ev, elapsed):
        pass
        #self.entity.component('position').node.translate(ev.channel.dir)
        #self.entity.component('light').content.point.position += ev.channel.dir

class Game(cubeapp.game.Game):

    bindings = {
        'keyboard': {
            'up': KeySym.up,
            'down': KeySym.down,
            'left': KeySym.left,
            'right': KeySym.right,
        },
    }

    def __init__(self, window, directory):
        super().__init__(window, directory, bindings = self.bindings)
        self.ground = ground.create(self)
        self.player = player.create(self)
        self.darklings = [
            darkling.create(self, x, y) for x, y in [
                (-5, 0),
                (-5, -10),
                (5, 0),
                (5, -10),
            ]
        ]
        self.camera = gl.Camera()
        self.__bind_camera_controls()
        self.scene_view = self.scene.drawable(self.renderer)

    def __bind_camera_controls(self):
        camera_controller = CameraController(self.camera)
        self.event_manager.add(camera_controller)
        kb = self.input_translator.keyboard
        for slot, chan in (
            (kb.up.key_held,    camera_controller.move_up),
            (kb.down.key_held,  camera_controller.move_down),
            (kb.left.key_held,  camera_controller.move_left),
            (kb.right.key_held, camera_controller.move_right),
        ):
            slot.connect(
                lambda _: self.event_manager.push(Event(chan))
            )


    def render(self):
        with self.renderer.begin(gl.mode_3d) as painter:
            painter.state.look_at(
                gl.vec3f(.5, 10, 10), gl.vec3f(0, 0, -10), gl.vec3f(0, 1, 0)
            )
            painter.state.perspective(
                units.deg(45), self.window.width / self.window.height, 0.005, 300.0
            )
            painter.draw([self.scene_view])
