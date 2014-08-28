
import cubeapp.world
from cubeapp.game.entity import component

class WorldController:

    def __init__(self, game):
        self.world = cubeapp.world.World(game.renderer)
        self.referential = cubeapp.world.world.coord_type()
        self.game = game
        self.channels = ['tick', game.shutdown_channel]

    def __call__(self, ev, delta):
        if ev.channel == self.game.shutdown_channel:
            self.world.stop()
            return
        self.world.update(delta, self.game.camera, self.referential)

def create(game):
    world = game.entity_manager.create("world")
    world.add_component(component.Controller(WorldController(game)))
    return world
