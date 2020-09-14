import math
import bpy
import mathutils


def solve(max_disk):
    def move(max_disk, rod_from, rod_to):
        rod_other = next(iter(set(range(3)).difference({rod_from, rod_to})))
        if max_disk == 1:
            yield rod_from, rod_to
        else:
            yield from move(max_disk - 1, rod_from, rod_other)
            yield rod_from, rod_to
            yield from move(max_disk - 1, rod_other, rod_to)

    yield from move(max_disk, 0, 2)


def make_material(h, s, v):
    material = bpy.data.materials.new(name='Material')
    color = mathutils.Color()
    color.hsv = h, s, v
    material.diffuse_color = *color, 1
    return material


def make_cylinder(radius, depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=256, radius=radius, depth=depth)
    cylinder = bpy.context.active_object
    bpy.context.view_layer.objects.active = cylinder
    bpy.ops.object.modifier_add(type='BEVEL')
    return cylinder


def make_action(lst):
    action = bpy.data.actions.new(name="Action")
    for i in range(3):
        fcurve = action.fcurves.new(data_path="location", index=i)
        fcurve.keyframe_points.add(len(lst))
        for j, (frame, pos) in enumerate(lst):
            fcurve.keyframe_points[j].co = frame, pos[i]
            fcurve.keyframe_points[j].interpolation = 'CUBIC'
    return action


max_disk = 6
solution = list(solve(max_disk))

for obj in bpy.context.scene.objects:
    bpy.data.objects.remove(obj)

floor = make_cylinder(100, 1)
floor.data.materials.append(make_material(0, 0, 1))
floor.location = 0, 0, -0.5

move_frames = 60
disk_depth = 0.1

rods_data = [list(reversed(range(max_disk))), [], []]
animation = [[] for _ in range(max_disk)]
for move, (i, j) in enumerate(solution):
    disk_i = rods_data[i].pop()
    animation[disk_i].append((move * move_frames, ((i - 1) * 3, 0, disk_depth * (len(rods_data[i]) * 2 + 1))))
    animation[disk_i].append(((move + 1 / 3) * move_frames, ((i - 1) * 3, 0, 2.7)))
    animation[disk_i].append(((move + 2 / 3) * move_frames, ((j - 1) * 3, 0, 2.7)))
    animation[disk_i].append(((move + 1) * move_frames, ((j - 1) * 3, 0, disk_depth * (len(rods_data[j]) * 2 + 1))))
    rods_data[j].append(disk_i)

rods = [()] * 3
for i in range(3):
    rods[i] = make_cylinder(0.05, 2)
    rods[i].data.materials.append(make_material(0, 0, 0.7))
    rods[i].location = (i - 1) * 3, 0, 1

disks = [()] * max_disk
for i in range(max_disk):
    disks[i] = make_cylinder(0.3 + i / max_disk * 0.7, disk_depth * 2)
    disks[i].data.materials.append(make_material(i / max_disk, 1, 1))
    disks[i].animation_data_create()
    disks[i].animation_data.action = make_action(animation[i])

bpy.ops.object.light_add(type='SUN', radius=1, align='WORLD', location=[0, 0, 0], rotation=[0, 0.3, 0])
bpy.ops.object.camera_add(enter_editmode=False, align='WORLD', location=[0, -12, 4.3], rotation=[math.pi * 0.42, 0, 0])

bpy.context.scene.render.fps = 60
bpy.context.scene.frame_start = 0
bpy.context.scene.frame_current = 0
bpy.context.scene.frame_end = len(solution) * move_frames
