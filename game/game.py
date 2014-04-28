from cube import gl, gui
from cube.system.inputs import KeySym

from . import player
from . import ground

import cubeapp.game

class GameView(gui.widgets.Viewport):
    def __init__(self, game):
        super().__init__(tag = 'gameview', renderer = game.renderer)
        self.game = game

    def render(self, painter2d):
        with self.renderer.begin(gl.mode_3d) as painter:
            painter.state.look_at(
                gl.vec3f(0, 10, 15), gl.vec3f(0, 0, 0), gl.vec3f(0, 1, 0)
            )
            painter.state.perspective(
                45, self.game.window.width / self.game.window.height, 0.005, 300.0
            )
            #print('#' * 40, 'START DRAWING')
            painter.draw([self.game.scene])
            #print('*' * 40, 'END DRAWING')

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
        self.view = GameView(self)
        self.ground = ground.create(self)
        self.player = player.create(self)
