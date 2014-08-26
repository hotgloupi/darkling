from cube import gl

import cubeapp.game
from cubeapp.game.event import Channel, Event
from cubeapp.game.entity.component import Transform, Component, Bindable, Drawable, Controller
from cubeapp.game.entity.system import System

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
    def change_colors(ev, delta):
        mat.ambiant = rand_color()
    player.add_component(Controller(change_colors, ['tick']))
    return player
