from cube import gl, gui, units, log
from cube.system.inputs import KeySym, KeyMod

from . import player
from . import ground
from . import darkling

import cubeapp.game
from cubeapp.game.entity.component import Controller, Transform, Bindable, Drawable
from cubeapp.game.event import Channel, Event
import cubeapp.world

import pathlib
import time

class CameraController:

    def __init__(self, cam, mouse, velocity = 40):
        super().__init__()
        self.move_left =  Channel()
        self.move_right = Channel()
        self.move_forward =    Channel()
        self.move_backward =  Channel()
        self.move_up =    Channel(dir = gl.vec3f(0, 1, 0))
        self.move_down =  Channel(dir = gl.vec3f(0, -1, 0))
        self.mouse_move = Channel()
        self.channels = [
            self.move_left,
            self.move_right,
            self.move_up,
            self.move_down,
            self.move_forward,
            self.move_backward,
            self.mouse_move,
            Channel('tick'),
        ]
        self.camera = cam
        self.mouse = mouse
        self.velocity = velocity
        self.dir = gl.vec3f()

    def __call__(self, ev, elapsed):
        if ev.channel == 'tick':
            if self.dir:
                self.camera.move(self.dir * elapsed * self.velocity)
                self.dir = self.dir * .8
            self.camera.rotate(units.deg(self.mouse.yrel / 10), self.camera.right)
            self.camera.rotate(units.deg(self.mouse.xrel / 10), gl.vec3f(0, 1, 0))
        else:
            if hasattr(ev.channel, 'dir'):
                dir = ev.channel.dir
            else:
                if ev.channel == self.move_left:
                    dir = -self.camera.right
                elif ev.channel == self.move_right:
                    dir = self.camera.right
                elif ev.channel == self.move_forward:
                    dir = self.camera.front
                elif ev.channel == self.move_backward:
                    dir = -self.camera.front
                dir.y = 0
            self.dir = gl.vector.normalize(self.dir + dir)


class Game(cubeapp.game.Game):

    bindings = {
        'keyboard': {
            'forward': KeySym.up,
            'backward': KeySym.down,
            'left': KeySym.left,
            'right': KeySym.right,
            'up': (KeySym.up, KeyMod.ctrl),
            'down': (KeySym.down, KeyMod.ctrl),
        },
    }

    def __init__(self, window, directory):
        super().__init__(window, directory, bindings = self.bindings)
        #self.ground = ground.create(self)
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
        self.camera.position = gl.vec3f(.5, 10, 10)
        self.camera.look_at(gl.vec3f(0, 0, -40))
        self.camera.init_frustum(
            units.deg(45), self.window.width / self.window.height, 0.005, 300.0
        )
        self.__bind_camera_controls()
        self.scene_view = self.scene.drawable(self.renderer)
        self.world = cubeapp.world.World(
            storage = cubeapp.world.Storage(),
            generator = cubeapp.world.Generator(),
            renderer = cubeapp.world.Renderer(self.renderer),
        )
        self.referential = cubeapp.world.world.coord_type()
        self.__has_focus = False
        self.window.inputs.on_mousedown.connect(self.__enter)
        self.__enter()
        self.world.start(self.camera, self.referential)


    def __enter(self, *args):
        if self.__has_focus:
            return
        self.__has_focus = True
        self.window.system_window.confine_mouse(True)

    def _on_quit(self):
        if self.__has_focus:
            self.window.system_window.confine_mouse(False)
            def disable_focus(elapsed):
                self.__has_focus = False
            self.event_manager.call_later(disable_focus, .5)
        else:
            super()._on_quit()

    def __del__(self):
        del self.scene_view
        del self.camera
        del self.player
        del self.darklings

    def __bind_camera_controls(self):
        camera_controller = CameraController(self.camera, self.input_translator.mouse)
        self.event_manager.add(camera_controller)
        kb = self.input_translator.keyboard
        for slot, chan in (
            (kb.up.key_held,    camera_controller.move_up),
            (kb.down.key_held,  camera_controller.move_down),
            (kb.forward.key_held,    camera_controller.move_forward),
            (kb.backward.key_held,  camera_controller.move_backward),
            (kb.left.key_held,  camera_controller.move_left),
            (kb.right.key_held, camera_controller.move_right),
        ):
            self.__bind_slot(slot, chan)

    def __bind_slot(self, slot, chan):
        def f(ev): self.event_manager.push(Event(chan))
        slot.connect(f)

    def shutdown(self):
        super().shutdown()
        self.world.stop()
        self.world = None

    def render(self):
        start = time.time()
        with self.renderer.begin(gl.mode_3d) as painter:
            with painter.bind([self.camera]):
                self.world.render(painter)
                painter.draw([self.scene_view])
        #log.info('render time %.2f ms' % ((time.time() - start) * 1000))


    def update(self, delta):
        start = time.time()
        diff = self.camera.position / cubeapp.world.Chunk.size
        int_diff = cubeapp.world.world.coord_type(
            diff.x, diff.y, diff.z
        )
        #self.referential += int_diff
        self.referential = int_diff
        #self.camera.position -= gl.vec3f(
        #    int_diff.x, int_diff.y, int_diff.z
        #) * cubeapp.world.Chunk.size

        self.world.update(self.camera, self.referential)
        #log.info('update time %.2f ms' % ((time.time() - start) * 1000))
        #print(self.scene.graph.root.children)
        super().update(delta)
