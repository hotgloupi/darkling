
from cube import gl, units, gui
from cubeapp.game import Game as BaseGame
from cubeapp.game.entity import component
from cube.system.inputs import KeySym

def create_ground(game):
    mat = gl.Material('ground')
    mat.ambient = gl.col3f('brown')
    mat.diffuse = gl.col3f('white')
    mat.specular = gl.col3f('white')
    mat.shading_model = gl.material.ShadingModel.gouraud
    mesh = gl.Mesh()
    mesh.mode = gl.DrawMode.quads
    mesh.append(gl.vec3f(-1, 1, 0))
    mesh.append(gl.vec3f(-1, -1, 0))
    mesh.append(gl.vec3f(1, -1, 0))
    mesh.append(gl.vec3f(1, 1, 0))
    return game.entity_manager.add(
        'ground',
        component.Transform,
        (component.View, {'parent_node': 'transform.node'}),
        transform = {
            'transformation':
                gl.matrix.rotate(
                    gl.matrix.translate(
                        gl.matrix.scale(gl.mat4f(), gl.vec3f(10)),
                        gl.vec3f(0, -1, 0)
                    ),
                    units.deg(-90),
                    gl.vec3f(1, 0, 0)
                )
        },
        view = {
            'contents': (mat, mesh),
        },
    )

from cubeapp.game import Controller
class PlayerController(Controller):

    def __init__(self):
        pass

def create_player(game):
    mat = gl.Material('player')
    mat.ambient = gl.col3f('pink')
    mat.diffuse = gl.col3f('white')
    mat.specular = gl.col3f('white')
    mesh = gl.Spheref(gl.vec3f(0), 1)
    light = game.renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    return game.entity_manager.add(
        'player',
        component.Transform,
        (component.View, {'parent_node': 'transform.node'}),
        view = {
            'contents': (light, mat, mesh),
        },
        transform = {
            'transformation': gl.matrix.translate(gl.mat4f(), gl.vec3f(0, -3.5, 0))
        }
    )

class GameView(gui.widgets.Viewport):
    def __init__(self, game):
        super().__init__(tag = 'gameview', renderer = game.renderer)
        self.game = game

    def render(self, painter2d):
        with self.renderer.begin(gl.mode_3d) as painter:
            painter.state.look_at(
                gl.vec3f(0, 5, 5), gl.vec3f(0, 0, 0), gl.vec3f(0, 1, 0)
            )
            painter.state.perspective(
                45, self.game.window.width / self.game.window.height, 0.005, 300.0
            )
            #print('#' * 40, 'START DRAWING')
            painter.draw([self.game.scene])
            #print('*' * 40, 'END DRAWING')

class Game(BaseGame):

    bindings = {
        'keyboard': {
            'up': KeySym.up,
            'down': KeySym.down,
            'left': KeySym.left,
            'right': KeySym.right,
        },
    }

    def __init__(self, window):
        super().__init__(window, bindings = self.bindings)
        self.view = GameView(self)
        self.ground = create_ground(self)
        self.player = create_player(self)
