import math
import bpy
import bpy_extras
import mathutils

for obj in bpy.context.scene.objects:
    bpy.data.objects.remove(obj)


def make_mesh(polygons):
    vertices, edges, faces = [], [], []
    for polygon in polygons:
        face = []
        for vertex in polygon:
            face.append(len(vertices))
            vertices.append(vertex)
        faces.append(face)
    mesh = bpy.data.meshes.new(name="Mesh")
    mesh.from_pydata(vertices, edges, faces)
    bpy_extras.object_utils.object_data_add(bpy.context, mesh)
    return mesh


def pyramid_polygons():
    polygons = []

    def go(s, a, b, c, d, n):
        if n == 1:
            polygons.append([a, b, c, d])
            polygons.append([a, b, s])
            polygons.append([b, c, s])
            polygons.append([c, d, s])
            polygons.append([d, a, s])
        else:
            go(s, (s + a) / 2, (s + b) / 2, (s + c) / 2, (s + d) / 2, n - 1)
            go((s + a) / 2, a, (a + b) / 2, (a + b + c + d) / 4, (a + d) / 2, n - 1)
            go((s + b) / 2, (a + b) / 2, b, (b + c) / 2, (a + b + c + d) / 4, n - 1)
            go((s + c) / 2, (a + b + c + d) / 4, (b + c) / 2, c, (c + d) / 2, n - 1)
            go((s + d) / 2, (c + d) / 2, (a + b + c + d) / 4, (a + d) / 2, d, n - 1)

    go(
        mathutils.Vector((0, 0, math.sqrt(2))),
        mathutils.Vector((-1, 1, 0)),
        mathutils.Vector((1, 1, 0)),
        mathutils.Vector((1, -1, 0)),
        mathutils.Vector((-1, -1, 0)),
        8,
    )

    return polygons


bpy.context.scene.render.engine = 'CYCLES'
make_mesh(pyramid_polygons())
bpy.ops.object.light_add(type='SPOT', radius=10, align='WORLD', location=[-0.8, 2.5, 9.4], rotation=[-0.3, -0.1, -0.1])
bpy.context.object.data.energy = 10000
bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=[1.2, -5.5, 3], rotation=[1.13, 0, 0.22])
