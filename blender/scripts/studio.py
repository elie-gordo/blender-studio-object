"""Studio: cyclorama backdrop, soft-box lighting, cameras, render settings."""
import math

import bmesh
import bpy
from mathutils import Vector

from common import empty, mesh_object, track_to

TARGET = (0, -0.06, 0.28)

# name: (location, size, energy W, color)
SOFTBOXES = {
    "LGT_Key": ((-1.3, -1.2, 1.5), 1.2, 110, (1.0, 0.97, 0.93)),
    "LGT_Fill": ((1.6, -1.1, 0.7), 1.8, 35, (0.93, 0.96, 1.0)),
    "LGT_Rim": ((0.9, 1.0, 1.4), 0.8, 90, (1.0, 1.0, 1.0)),
}

# name: (location, focal mm, aim point, f-stop)
CAMERAS = {
    "CAM_Hero": ((1.05, -2.05, 0.66), 70, (-0.08, -0.06, 0.25), 8.0),
    "CAM_Profile": ((0.19, -2.25, 0.34), 70, (0.19, 0.03, 0.27), 8.0),  # with lamp yaw 90
    "CAM_Detail": ((0.30, -0.42, 0.24), 100, (0.0, 0.0, 0.13), 4.0),
    "CAM_Anim": ((1.0, -2.15, 0.58), 65, (-0.10, -0.06, 0.24), 8.0),
    "CAM_Overview": ((3.2, -4.6, 2.9), 24, (0.0, -0.3, 0.6), 16.0),  # making-of: shows the soft boxes
}


def _cyclorama(coll, mat, width=8.0, depth=4.0, height=3.0, radius=0.9, back_y=1.6, steps=16):
    """Floor sweeping into a back wall with a large fillet (no visible horizon)."""
    profile = [(back_y - depth - radius, 0.0)]
    for i in range(steps + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / steps
        profile.append((back_y - radius + radius * math.cos(a), radius + radius * math.sin(a)))
    profile.append((back_y, height))
    bm = bmesh.new()
    rows = [[bm.verts.new((x, y, z)) for y, z in profile] for x in (-width / 2, width / 2)]
    for j in range(len(profile) - 1):
        bm.faces.new((rows[0][j], rows[1][j], rows[1][j + 1], rows[0][j + 1]))
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    if bm.faces[0].normal.z < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return mesh_object("Studio_Cyclorama", bm, coll, mat, smooth=True)


def _area(name, coll, loc, size, energy, color, target):
    data = bpy.data.lights.new(name, "AREA")
    data.shape = "DISK"
    data.size = size
    data.energy = energy
    data.color = color
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    obj.location = loc
    track_to(obj, target)
    return obj


def _camera(name, coll, loc, focal, aim_at, fstop):
    target = empty(f"{name}_Target", coll, None, aim_at, 0.03)
    data = bpy.data.cameras.new(name)
    data.lens = focal
    data.dof.use_dof = True
    data.dof.focus_object = target
    data.dof.aperture_fstop = fstop
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    obj.location = loc
    track_to(obj, target)
    return obj


def _world():
    world = bpy.data.worlds.new("WLD_Studio")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
    bg.inputs["Strength"].default_value = 0.06
    bpy.context.scene.world = world


def configure_render(scene, samples=256, res=(1920, 1080)):
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.refresh_devices()
    for dev in prefs.devices:
        dev.use = dev.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.denoiser = "OPTIX"
    scene.cycles.max_bounces = 8
    scene.cycles.caustics_reflective = False
    scene.cycles.caustics_refractive = False
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"


def build(mats, coll):
    target = empty("Studio_Target", coll, None, TARGET, 0.05)
    _cyclorama(coll, mats["backdrop"])
    lights = {n: _area(n, coll, loc, size, e, col, target) for n, (loc, size, e, col) in SOFTBOXES.items()}
    cams = {n: _camera(n, coll, *spec) for n, spec in CAMERAS.items()}
    _world()
    scene = bpy.context.scene
    scene.camera = cams["CAM_Hero"]
    configure_render(scene)
    return {"target": target, "lights": lights, "cameras": cams}


def aim(camera_name, target_loc):
    """Retarget one camera without moving the shared studio target."""
    cam = bpy.data.objects[camera_name]
    tgt = bpy.data.objects.get(f"{camera_name}_Target") or empty(f"{camera_name}_Target", cam.users_collection[0])
    tgt.location = Vector(target_loc)
    cam.constraints["Track To"].target = tgt
    cam.data.dof.focus_object = tgt
