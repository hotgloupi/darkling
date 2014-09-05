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

    def __init__(self, cam, velocity = 40):
        super().__init__()
        self.move_left =  Channel(dir = gl.vec3f(-1, 0, 0))
        self.move_right = Channel(dir = gl.vec3f(1, 0, 0))
        self.move_forward =    Channel(dir = gl.vec3f(0, 0, -1))
        self.move_backward =  Channel(dir = gl.vec3f(0, 0, 1))
        self.move_up =    Channel(dir = gl.vec3f(0, 1, 0))
        self.move_down =  Channel(dir = gl.vec3f(0, -1, 0))
        self.channels = [
            self.move_left,
            self.move_right,
            self.move_up,
            self.move_down,
            self.move_forward,
            self.move_backward,
            Channel('tick'),
        ]
        self.camera = cam
        self.velocity = velocity
        self.dir = gl.vec3f()

    def __call__(self, ev, elapsed):
        if ev.channel == 'tick':
            if self.dir:
                self.camera.move(self.dir * elapsed * self.velocity)
                self.dir = self.dir * .8
        else:
            self.dir = gl.vector.normalize(self.dir + ev.channel.dir)

class WorldController:

    def __init__(self, game, add_channel, del_channel):
        self.game = game
        self.add_channel = add_channel
        self.del_channel = del_channel
        self.channels = [add_channel, del_channel]
        mat1 = gl.Material('ground')
        mat1.ambient = gl.col3f('#200')
        mat1.diffuse = gl.col3f('brown')
        mat1.specular = gl.col3f('gray')
        mat1.shininess = 1000
        mat1.shading_model = gl.material.ShadingModel.gouraud
        mat1.add_texture(
            "ground.bmp",
            gl.TextureType.ambient,
            gl.TextureMapping.uv,
            gl.StackOperation.add,
            gl.TextureMapMode.wrap,
            gl.BlendMode.basic
        )
        mat2 = gl.Material('ground')
        mat2.ambient = gl.col3f('#022')
        mat2.diffuse = gl.col3f('brown')
        mat2.specular = gl.col3f('gray')
        mat2.shininess = 1000
        mat2.shading_model = gl.material.ShadingModel.gouraud
        mat2.add_texture(
            "ground.bmp",
            gl.TextureType.ambient,
            gl.TextureMapping.uv,
            gl.StackOperation.add,
            gl.TextureMapMode.wrap,
            gl.BlendMode.basic
        )
        self.material1 = mat1.bindable(game.renderer)
        self.material2 = mat2.bindable(game.renderer)
        mesh = gl.Mesh()
        mesh.mode = gl.DrawMode.quads
        size = 40
        step = 1.0 / size
        for i in (i / size for i in range(size)):
            x = i
            for j in (i / size for i in range(size)):
                y = 1.0 - j
                mesh.kind = gl.ContentKind.vertex
                mesh.append(gl.vec3f(x, 0, y - step))
                mesh.append(gl.vec3f(x, 0, y))
                mesh.append(gl.vec3f(x + step, 0, y))
                mesh.append(gl.vec3f(x + step, 0, y - step))
                mesh.kind = gl.ContentKind.tex_coord0
                mesh.append(gl.vec2f(i, j + step))
                mesh.append(gl.vec2f(i + step, j + step))
                mesh.append(gl.vec2f(i + step, j))
                mesh.append(gl.vec2f(i, j))
                mesh.kind = gl.ContentKind.normal
                mesh.append(gl.vec3f(0, 1, 0))
                mesh.append(gl.vec3f(0, 1, 0))
                mesh.append(gl.vec3f(0, 1, 0))
                mesh.append(gl.vec3f(0, 1, 0))
        self.mesh = mesh.drawable(game.renderer)
        self.entities = {}

    def __call__(self, ev, elapsed):
        if ev.channel == self.add_channel:
            self.add(ev.chunk)
        elif ev.channel == self.del_channel:
            self.remove(ev.chunk)

    def add(self, chunk):
        #if  chunk.node.size > 64: return
        if chunk.node.origin.y != 0: return
        entity = self.game.entity_manager.create("chunk")
        entity.add_component(
            Transform(
                gl.matrix.scale(
                    gl.matrix.translate(
                        gl.mat4f(),
                        gl.vec3f(
                            chunk.node.origin.x * chunk.size,
                            chunk.node.origin.y * chunk.size,
                            chunk.node.origin.z * chunk.size
                        )
                    )
                    , gl.vec3f(chunk.node.size * chunk.size)
                )
            )
                #gl.matrix.rotate(
                #    gl.matrix.translate(
                #        gl.matrix.scale(gl.mat4f(), gl.vec3f(20)),
                #        gl.vec3f(-.5, 0, 0)
                #    ),
                #    units.deg(-90),
                #    gl.vec3f(1, 0, 0)
                #)
        )
        if chunk.node.size == 1:
            entity.add_component(Bindable(self.material1))
        else:
            entity.add_component(Bindable(self.material2))
        entity.add_component(Drawable(self.mesh))
        self.entities[chunk.node] = entity
        #print("ADD", chunk)

    def remove(self, chunk):
        #print("REMOVE", chunk)
        if chunk.node in self.entities:
            self.entities[chunk.node].destroy()
            del self.entities[chunk.node]
        #else:
        #    print("Unknown chunk", chunk)

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
        self.__remove_chunk = Channel()
        self.__add_chunk = Channel()
        self.event_manager.add(WorldController(self, self.__add_chunk, self.__remove_chunk))
        self.world = cubeapp.world.World(self.renderer)
        self.referential = cubeapp.world.world.coord_type()
        self.__has_focus = False
        self.window.inputs.on_mousedown.connect(self.__enter)
        self.world.start(self.camera, self.referential)
        self.__enter()


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
        camera_controller = CameraController(self.camera)
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
                painter.draw([self.scene_view])
        #log.info('render time %.2f ms' % ((time.time() - start) * 1000))


    def update(self, delta):
        start = time.time()
        self.world.update(self.camera, self.referential)
        to_remove, to_add = self.world.poll()
        for chunk in to_remove:
            self.event_manager.push(Event(self.__remove_chunk, chunk = chunk))
        for chunk in to_add:
            self.event_manager.push(Event(self.__add_chunk, chunk = chunk))
        #log.info('update time %.2f ms' % ((time.time() - start) * 1000))
        super().update(delta)
