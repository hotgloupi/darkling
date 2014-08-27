
import cubeapp.world
from cubeapp.game.entity import component

class WorldController:
    channels = ['tick']

    def __init__(self, game):
        self.world = cubeapp.world.World(game.renderer)

    def __call__(self, ev, delta):
        pass

def create(game):
    world = game.entity_manager.create("world")
    world.add_component(component.Controller(WorldController(game)))
    return world
