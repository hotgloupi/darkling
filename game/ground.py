from cube import gl, units

import cubeapp.game

def create(game):
    mat = gl.Material('ground')
    mat.ambient = gl.col3f('black')
    mat.diffuse = gl.col3f('brown')
    mat.specular = gl.col3f('gray')
    mat.shininess = 1000
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
    size = 40
    step = 1.0 / size
    for i in (i / size for i in range(size)):
        x = i
        for j in (i / size for i in range(size)):
            y = 1.0 - j
            mesh.kind = gl.ContentKind.vertex
            mesh.append(gl.vec3f(x, y, 0))
            mesh.append(gl.vec3f(x, y - step, 0))
            mesh.append(gl.vec3f(x + step, y - step, 0))
            mesh.append(gl.vec3f(x + step, y, 0))
            mesh.kind = gl.ContentKind.tex_coord0
            mesh.append(gl.vec2f(i, j))
            mesh.append(gl.vec2f(i, j + step))
            mesh.append(gl.vec2f(i + step, j + step))
            mesh.append(gl.vec2f(i + step, j))
            mesh.kind = gl.ContentKind.normal
            mesh.append(gl.vec3f(0, 0, 1))
            mesh.append(gl.vec3f(0, 0, 1))
            mesh.append(gl.vec3f(0, 0, 1))
            mesh.append(gl.vec3f(0, 0, 1))
    light = game.renderer.new_light(
        gl.PointLightInfo(
            gl.vec3f(0, 2, -1),
            gl.Color3f("#888"),
            gl.Color3f("#333"),
        )
    )
    ground = game.entity_manager.create("ground")
    ground.add_component(
        cubeapp.game.entity.component.Transform(
            gl.matrix.rotate(
                gl.matrix.translate(
                    gl.matrix.scale(gl.mat4f(), gl.vec3f(20)),
                    gl.vec3f(-.5, 0, 0)
                ),
                units.deg(-90),
                gl.vec3f(1, 0, 0)
            )
        )
    )
    ground.add_component(
        cubeapp.game.entity.component.Bindable(mat)
    )
    ground.add_component(
        cubeapp.game.entity.component.Drawable(mesh)
    )
    return ground
