"""Shared helpers for building the TENSIL scene with bpy + bmesh."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

SMOOTH_ANGLE = math.radians(35)


def collection(name):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def mesh_object(name, bm, coll, material=None, parent=None, location=(0, 0, 0), smooth=True):
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
        mesh.set_sharp_from_angle(angle=SMOOTH_ANGLE)
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    obj.parent = parent
    obj.location = location
    return obj


def empty(name, coll, parent=None, location=(0, 0, 0), size=0.02):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = size
    coll.objects.link(obj)
    obj.parent = parent
    obj.location = location
    return obj


def bevel(obj, width, segments=3, angle=30):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.angle_limit = math.radians(angle)
    mod.harden_normals = True
    return mod


def cylinder(radius, depth, segments=48, axis="Z", center=(0, 0, 0), radius_top=None):
    """Capped cylinder (or cone frustum) centered on `center`, aligned to `axis`."""
    bm = bmesh.new()
    rot = {"Z": Matrix(), "X": Matrix.Rotation(math.radians(90), 4, "Y"),
           "Y": Matrix.Rotation(math.radians(90), 4, "X")}[axis]
    bmesh.ops.create_cone(
        bm, cap_ends=True, segments=segments, radius1=radius,
        radius2=radius if radius_top is None else radius_top, depth=depth,
        matrix=Matrix.Translation(Vector(center)) @ rot,
    )
    return bm


def box(size, center=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation(Vector(center)) @ Matrix.Diagonal((*size, 1)))
    return bm


def merge(*bms):
    """Merge several bmesh objects into a new one (sources are freed)."""
    out = bmesh.new()
    for src in bms:
        tmp = bpy.data.meshes.new("_tmp")
        src.to_mesh(tmp)
        src.free()
        out.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    return out


def lathe(profile, segments=96):
    """Revolve a (radius, z) polyline around Z into an open surface with outward normals."""
    bm = bmesh.new()
    rings = []
    for i in range(segments):
        a = 2 * math.pi * i / segments
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
    for i in range(segments):
        ring, nxt = rings[i], rings[(i + 1) % segments]
        for j in range(len(profile) - 1):
            bm.faces.new((ring[j], nxt[j], nxt[j + 1], ring[j + 1]))
    bm.normal_update()
    flip = []
    for face in bm.faces:
        c = face.calc_center_median()
        if face.normal.dot(Vector((c.x, c.y, 0))) < 0:
            flip.append(face)
    bmesh.ops.reverse_faces(bm, faces=flip)
    return bm


def curve_to_mesh_object(name, curve_obj, coll, material, parent=None):
    """Bake an evaluated curve object into a mesh object, then delete the curve."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(curve_obj.evaluated_get(depsgraph))
    mesh.name = name
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    coll.objects.link(obj)
    obj.data.materials.clear()
    obj.data.materials.append(material)
    obj.parent = parent
    obj.matrix_world = curve_obj.matrix_world.copy()
    curve_data = curve_obj.data
    bpy.data.objects.remove(curve_obj)
    bpy.data.curves.remove(curve_data)
    return obj


def track_to(obj, target):
    con = obj.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    return con
