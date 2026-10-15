"""TENSIL lamp geometry and rig.

Units: metres. The arm works in the local YZ plane; positive X-rotation tilts
a segment toward -Y (the lamp's front). Rig hierarchy:
    RIG_Yaw (turret, Z) > RIG_Shoulder (X) > RIG_Elbow (X) > RIG_Wrist (X)
"""
import math

import bmesh
import bpy
from mathutils import Vector

from common import bevel, box, curve_to_mesh_object, cylinder, empty, lathe, merge, mesh_object

BASE_R, BASE_TOP = 0.11, 0.030
TURRET_Y = 0.03
SHOULDER_Z = 0.060          # above turret origin
L1, L2 = 0.30, 0.30         # lower / upper arm lengths
TAIL = 0.045                # upper-arm lever behind the elbow
ROD_R = 0.0042
LOWER_X, UPPER_X, SPRING_X = 0.009, 0.0165, 0.029

# (yaw, shoulder, elbow, wrist) in degrees
POSES = {
    "rest": (0, 0, 0, 0),
    "folded": (0, -10, 130, 30),
    "work": (0, 15, 68, 80),
}


# ---------------------------------------------------------------- parts
def _boss_pair(x, z, radius=0.0095, width=0.006):
    return merge(*(cylinder(radius, width, 32, "X", (s * x, 0, z)) for s in (1, -1)))


def _rods(x, z0, z1):
    mid, depth = (z0 + z1) / 2, z1 - z0
    return merge(*(cylinder(ROD_R, depth, 24, "Z", (s * x, 0, mid)) for s in (1, -1)))


def _pins(x0, x1, y, z):
    c, w = (x0 + x1) / 2, x1 - x0
    return merge(*(cylinder(0.0022, w, 16, "X", (s * c, y, z)) for s in (1, -1)))


def _pivot_bolt(z, half_width):
    """Through-bolt with a knurled-looking knob on +X and a cap on -X."""
    return merge(
        cylinder(0.0032, 2 * half_width, 24, "X", (0, 0, z)),
        cylinder(0.0085, 0.007, 40, "X", (half_width + 0.0035, 0, z)),
        cylinder(0.0055, 0.003, 32, "X", (-half_width - 0.0015, 0, z)),
    )


def _base(coll, mats):
    body = mesh_object("Base_Body", cylinder(BASE_R, 0.026, 96, center=(0, 0, 0.017), radius_top=0.104),
                       coll, mats["lacquer"])
    bevel(body, 0.003, 4)
    mesh_object("Base_Foot", cylinder(0.103, 0.004, 96, center=(0, 0, 0.002)), coll, mats["rubber"])

    a = math.radians(-62)
    knob = mesh_object("Base_SwitchKnob", merge(cylinder(0.006, 0.010, 32, "Y", (0, 0.004, 0)),
                                                cylinder(0.0035, 0.004, 24, "Y", (0, -0.002, 0))),
                       coll, mats["brass"], location=(0.106 * math.cos(a), 0.106 * math.sin(a), 0.016))
    knob.rotation_euler.z = a - math.pi / 2
    bevel(knob, 0.0008, 2)

    relief = mesh_object("Base_CableGland", cylinder(0.0045, 0.012, 24, "Y", (0, 0.108, 0.012)),
                         coll, mats["rubber"])
    bevel(relief, 0.001, 2)
    _logo(coll, mats)
    _cable(coll, mats)
    return body


def _logo(coll, mats):
    text = bpy.data.curves.new("TXT_Logo", "FONT")
    text.body = "TENSIL"
    text.size = 0.0125
    text.space_character = 1.45
    text.extrude = 0.00035
    text.align_x = "CENTER"
    obj = bpy.data.objects.new("TMP_Logo", text)
    coll.objects.link(obj)
    obj.location = (0, -0.07, BASE_TOP + 0.0002)
    curve_to_mesh_object("Base_Logo", obj, coll, mats["brass"])


def _cable(coll, mats):
    curve = bpy.data.curves.new("CRV_Cable", "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.0024
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    pts = [(0, 0.114, 0.012), (0, 0.16, 0.0024), (-0.04, 0.40, 0.0024), (-0.02, 0.80, 0.0024)]
    spline.bezier_points.add(len(pts) - 1)
    for bp, co in zip(spline.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new("TMP_Cable", curve)
    coll.objects.link(obj)
    curve_to_mesh_object("Base_Cable", obj, coll, mats["rubber"])


def _turret(coll, mats, yaw):
    body = mesh_object("Turret_Body", merge(
        cylinder(0.027, 0.028, 64, center=(0, 0, 0.014)),
        cylinder(0.030, 0.004, 64, center=(0, 0, 0.002)),
    ), coll, mats["lacquer"], parent=yaw)
    bevel(body, 0.0015, 3)
    plates = mesh_object("Turret_Fork", merge(*(
        part for s in (1, -1) for part in (
            box((0.004, 0.034, 0.032), (s * 0.0175, 0.012, 0.040)),
            cylinder(0.017, 0.004, 48, "X", (s * 0.0175, 0.012, 0.046)),
            cylinder(0.0125, 0.004, 40, "X", (s * 0.0175, 0.0, SHOULDER_Z)),
        )
    )), coll, mats["metal"], parent=yaw)
    bevel(plates, 0.0012, 3)
    mesh_object("Turret_Bolt", _pivot_bolt(SHOULDER_Z, 0.0195), coll, mats["brass"], parent=yaw)
    mesh_object("Turret_SpringPins", _pins(0.0195, SPRING_X + 0.003, 0.030, 0.046), coll, mats["metal"], parent=yaw)


def _lower_arm(coll, mats, shoulder):
    arm = mesh_object("LowerArm_Rods", merge(
        _rods(LOWER_X, 0.0, L1),
        _boss_pair(LOWER_X, 0.0), _boss_pair(LOWER_X, L1),
        box((2 * LOWER_X, 0.006, 0.012), (0, 0, L1 * 0.5)),
    ), coll, mats["lacquer"], parent=shoulder)
    bevel(arm, 0.001, 2)
    mesh_object("LowerArm_SpringPins", merge(
        _pins(LOWER_X, SPRING_X + 0.003, 0, 0.11),
        _pins(LOWER_X, SPRING_X + 0.003, 0, L1 - 0.22),
    ), coll, mats["metal"], parent=shoulder)


def _upper_arm(coll, mats, elbow):
    arm = mesh_object("UpperArm_Rods", merge(
        _rods(UPPER_X, -TAIL, L2),
        _boss_pair(UPPER_X, 0.0), _boss_pair(UPPER_X, L2), _boss_pair(UPPER_X, -TAIL, 0.007),
        box((2 * UPPER_X, 0.006, 0.010), (0, 0, L2 * 0.55)),
    ), coll, mats["lacquer"], parent=elbow)
    bevel(arm, 0.001, 2)
    mesh_object("UpperArm_Bolt", _pivot_bolt(0.0, 0.0195), coll, mats["brass"], parent=elbow)
    mesh_object("UpperArm_SpringPins", _pins(UPPER_X, SPRING_X + 0.003, 0, -TAIL), coll, mats["metal"], parent=elbow)


def _head(coll, mats, wrist):
    shade_profile = [(0.0005, 0.030), (0.012, 0.031), (0.020, 0.036), (0.026, 0.048), (0.040, 0.076),
                     (0.056, 0.108), (0.069, 0.136), (0.075, 0.150), (0.0765, 0.154)]
    shade = mesh_object("Head_Shade", lathe(shade_profile, 128), coll, mats["lacquer"], parent=wrist)
    shade.data.materials.append(mats["reflector"])
    solid = shade.modifiers.new("Solidify", "SOLIDIFY")
    solid.thickness = 0.0016
    solid.offset = -1
    solid.use_rim = True
    solid.material_offset = 1
    solid.use_even_offset = True

    rim = lathe([(0.0765 + 0.0022 * math.cos(t), 0.154 + 0.0022 * math.sin(t))
                 for t in (2 * math.pi * i / 12 for i in range(13))], 128)
    bmesh.ops.remove_doubles(rim, verts=rim.verts, dist=1e-6)
    bmesh.ops.recalc_face_normals(rim, faces=rim.faces)
    mesh_object("Head_RimBead", rim, coll, mats["brass"], parent=wrist)

    neck = mesh_object("Head_Neck", merge(
        cylinder(0.011, 0.036, 48, center=(0, 0, 0.014)),
        cylinder(0.010, 2 * (UPPER_X - 0.003), 40, "X", (0, 0, 0)),
    ), coll, mats["brass"], parent=wrist)
    bevel(neck, 0.0008, 2)
    mesh_object("Head_Bolt", _pivot_bolt(0.0, UPPER_X + 0.003), coll, mats["brass"], parent=wrist)
    mesh_object("Head_Socket", cylinder(0.0135, 0.020, 48, center=(0, 0, 0.042)), coll, mats["reflector"], parent=wrist)

    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.023)
    bmesh.ops.scale(bm, vec=(1, 1, 1.18), verts=bm.verts)
    mesh_object("Head_Bulb", bm, coll, mats["bulb"], parent=wrist, location=(0, 0, 0.075))

    spot_data = bpy.data.lights.new("LGT_Bulb", "SPOT")
    spot_data.energy = 0.0
    spot_data.color = (1.0, 0.78, 0.52)
    spot_data.spot_size = math.radians(115)
    spot_data.spot_blend = 0.6
    spot_data.shadow_soft_size = 0.02
    spot = bpy.data.objects.new("LGT_Bulb", spot_data)
    coll.objects.link(spot)
    spot.parent = wrist
    spot.location = (0, 0, 0.10)
    spot.rotation_euler.x = math.pi
    return spot


# ---------------------------------------------------------------- springs
def _helix_curve(name, coll, length, coil_r=0.0052, wire_r=0.00105, turns=16, lead=0.008):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = wire_r
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    pts = [Vector((0, 0, 0)), Vector((0, lead * 0.6, 0))]
    coil_len = length - 2 * lead
    steps = turns * 20
    for i in range(steps + 1):
        t = i / steps
        a = 2 * math.pi * turns * t
        pts.append(Vector((coil_r * math.cos(a), lead + coil_len * t, coil_r * math.sin(a))))
    pts += [Vector((0, length - lead * 0.6, 0)), Vector((0, length, 0))]
    spline.points.add(len(pts) - 1)
    for p, co in zip(spline.points, pts):
        p.co = (*co, 1)
    obj = bpy.data.objects.new(name, curve)
    coll.objects.link(obj)
    return obj


def _spring(name, coll, mats, anchor_a, anchor_b):
    """Helix stretched between two anchor empties with a Stretch To constraint."""
    bpy.context.view_layer.update()
    length = (anchor_b.matrix_world.translation - anchor_a.matrix_world.translation).length
    crv = _helix_curve("TMP_" + name, coll, length)
    obj = curve_to_mesh_object(name, crv, coll, mats["spring"])
    obj.parent = anchor_a
    obj.matrix_world = anchor_a.matrix_world.copy()
    obj.location = (0, 0, 0)
    con = obj.constraints.new("STRETCH_TO")
    con.target = anchor_b
    con.rest_length = length
    con.volume = "NO_VOLUME"
    con.keep_axis = "PLANE_X"
    return obj


def _springs(coll, mats, rig):
    yaw, shoulder, elbow = rig["yaw"], rig["shoulder"], rig["elbow"]
    for side, s in (("L", 1), ("R", -1)):
        x = s * SPRING_X
        a1 = empty(f"ANC_Lower_A_{side}", coll, yaw, (x, 0.030, 0.046), 0.005)
        b1 = empty(f"ANC_Lower_B_{side}", coll, shoulder, (x, 0, 0.11), 0.005)
        a2 = empty(f"ANC_Upper_A_{side}", coll, elbow, (x, 0, -TAIL), 0.005)
        b2 = empty(f"ANC_Upper_B_{side}", coll, shoulder, (x, 0, L1 - 0.22), 0.005)
        _spring(f"Spring_Lower_{side}", coll, mats, a1, b1)
        _spring(f"Spring_Upper_{side}", coll, mats, a2, b2)


# ---------------------------------------------------------------- public API
def set_pose(rig, name_or_angles):
    angles = POSES[name_or_angles] if isinstance(name_or_angles, str) else name_or_angles
    yaw, sh, el, wr = (math.radians(a) for a in angles)
    rig["yaw"].rotation_euler.z = yaw
    rig["shoulder"].rotation_euler.x = sh
    rig["elbow"].rotation_euler.x = el
    rig["wrist"].rotation_euler.x = wr


def build(mats, coll):
    yaw = empty("RIG_Yaw", coll, None, (0, TURRET_Y, BASE_TOP), 0.06)
    shoulder = empty("RIG_Shoulder", coll, yaw, (0, 0, SHOULDER_Z), 0.05)
    elbow = empty("RIG_Elbow", coll, shoulder, (0, 0, L1), 0.05)
    wrist = empty("RIG_Wrist", coll, elbow, (0, 0, L2), 0.05)
    rig = {"yaw": yaw, "shoulder": shoulder, "elbow": elbow, "wrist": wrist}

    _base(coll, mats)
    _turret(coll, mats, yaw)
    _lower_arm(coll, mats, shoulder)
    _upper_arm(coll, mats, elbow)
    rig["bulb_light"] = _head(coll, mats, wrist)

    set_pose(rig, "work")
    _springs(coll, mats, rig)
    return rig
