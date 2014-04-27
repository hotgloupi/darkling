
from cube import gl, units, gui
from cubeapp import game

class Ground(game.entity.Entity):

    components = [
        game.entity.component.Transform,
        (game.entity.component.View, {'parent_node': 'transform.node'})
    ]


class GameView(gui.widgets.Viewport):
    def __init__(self, game):
        super().__init__(tag = 'gameview', renderer = game.renderer)
        self.game = game

    def render(self, painter2d):
        with self.renderer.begin(gl.mode_3d) as painter:
            painter.state.look_at(
                gl.vec3f(0, 0, -30), gl.vec3f(0, 0, 0), gl.vec3f(0, 1, 0)
            )
            painter.state.perspective(
                45, self.game.window.width / self.game.window.height, 0.005, 300.0
            )
            painter.draw([self.game.scene])

class Game(game.Game):

    def __init__(self, window):
        super().__init__(window)
        self.view = GameView(self)
        ground_mat = gl.Material('ground')
        ground_mat.ambient = gl.col3f('pink')
        ground_mat.diffuse = gl.col3f('white')
        ground_mat.specular = gl.col3f('white')
        ground_mesh = gl.Mesh()
        ground_mesh.append(gl.vec3f(-1, 1, -1))
        ground_mesh.append(gl.vec3f(-1, -1, -1))
        ground_mesh.append(gl.vec3f(1, -1, -1))
        ground_mesh.append(gl.vec3f(1, 1, -1))
        self.ground = self.entity_manager.add(
            Ground,
            transform = {
                'transformation': gl.matrix.rotate(gl.mat4f(), units.deg(90), gl.vec3f(1, 0, 0)),
            },
            view = {
                'contents': (ground_mat, ground_mesh),
            },
        )
