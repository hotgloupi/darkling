
from cube import gl, units

import cubeapp.game
from cubeapp.game.entity.component import Transform, View

def create(game, x, z):
    mat = gl.Material('player')
    mat.ambient = gl.col3f('#100')
    mat.diffuse = gl.col3f('#f55')
    mat.specular = gl.col3f('#f00')
    mat.shininess = .5
    mat.shading_model = gl.material.ShadingModel.gouraud

    mesh = gl.Spheref(gl.vec3f(0), 1).drawable(game.renderer)

    return game.entity_manager.add(
        'Darkling',
        Transform,
        (View, {'parent_node': 'transform.node'}),
        view = {
            'contents': (mat, mesh),
        },
        transform = {
            'transformation': gl.matrix.translate(gl.mat4f(), gl.vec3f(x, 1, z))
        },
    )
