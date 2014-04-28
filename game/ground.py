from cube import gl, units

import cubeapp.game

def create(game):
    mat = gl.Material('ground')
    mat.ambient = gl.col3f('blue')
    mat.diffuse = gl.col3f('red')
    mat.specular = gl.col3f('orange')
    mat.shininess = 0.1
    mat.shading_model = gl.material.ShadingModel.gouraud
    mat.add_texture(
        "ground.bmp",
        gl.TextureType.ambient,
        gl.TextureMapping.uv,
        gl.StackOperation.add,
        gl.TextureMapMode.wrap,
        gl.BlendMode.basic
    )
    mesh = gl.Mesh()
    mesh.mode = gl.DrawMode.quads
    mesh.append(gl.vec3f(-1, 1, 0))
    mesh.append(gl.vec3f(-1, -1, 0))
    mesh.append(gl.vec3f(1, -1, 0))
    mesh.append(gl.vec3f(1, 1, 0))
    mesh.kind = gl.ContentKind.tex_coord0
    mesh.append(gl.vec2f(0, 0))
    mesh.append(gl.vec2f(1, 0))
    mesh.append(gl.vec2f(1, 1))
    mesh.append(gl.vec2f(0, 1))
    light = game.renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0, 2, -1),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    return game.entity_manager.add(
        'ground',
        cubeapp.game.entity.component.Transform,
        (cubeapp.game.entity.component.View, {'parent_node': 'transform.node'}),
        transform = {
            'transformation':
                gl.matrix.rotate(
                    gl.matrix.translate(
                        gl.matrix.scale(gl.mat4f(), gl.vec3f(10)),
                        gl.vec3f(0, 0, 0)
                    ),
                    units.deg(-90),
                    gl.vec3f(1, 0, 0)
                )
        },
        view = {
            'contents': (light, mat, mesh),
        },
    )
