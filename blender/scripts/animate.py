"""Product animation: unfold from the folded pose, dim the studio, switch the bulb on."""
import math

import bpy

FPS = 30
FRAME_END = 240  # 8 s

# rig key: (axis, [(frame, degrees), ...]) — staggered so each joint leads the next
JOINT_KEYS = {
    "yaw": ("z", [(1, 0), (24, 0), (110, -20)]),
    "shoulder": ("x", [(1, -10), (20, -10), (92, 17), (104, 15)]),
    "elbow": ("x", [(1, 130), (30, 130), (100, 66), (112, 68)]),
    "wrist": ("x", [(1, 30), (48, 30), (112, 86), (126, 78), (136, 80)]),
}
# multiplier on studio light energy
STUDIO_KEYS = [(1, 1.0), (138, 1.0), (162, 0.18)]
# fraction of full bulb output: quick flicker then steady
BULB_KEYS = [(150, 0.0), (152, 0.7), (154, 0.15), (157, 0.9), (159, 0.5), (162, 1.0)]
CAMERA_PUSH = 0.06  # fraction of distance travelled toward the target over the shot


def _fcurves(anim):
    """F-curves of an action, supporting both legacy and layered (slotted) actions."""
    action = anim.action
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    curves = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            channelbag = strip.channelbag(anim.action_slot)
            if channelbag:
                curves.extend(channelbag.fcurves)
    return curves


def _ease(owner, interpolation="BEZIER", easing="AUTO"):
    anim = owner.animation_data
    if not anim or not anim.action:
        return
    for fc in _fcurves(anim):
        for kp in fc.keyframe_points:
            kp.interpolation = interpolation
            kp.easing = easing
            kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"


def _animate_rig(rig):
    for key, (axis, keys) in JOINT_KEYS.items():
        obj, idx = rig[key], "xyz".index(axis)
        for frame, deg in keys:
            obj.rotation_euler[idx] = math.radians(deg)
            obj.keyframe_insert("rotation_euler", index=idx, frame=frame)
        _ease(obj)


def _animate_studio(studio_lights):
    for light in studio_lights.values():
        base = light.data.energy
        for frame, mult in STUDIO_KEYS:
            light.data.energy = base * mult
            light.data.keyframe_insert("energy", frame=frame)
        _ease(light.data)


def _animate_bulb(rig, mats, bulb_on):
    socket = mats["bulb"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    spot = rig["bulb_light"].data
    for frame, frac in BULB_KEYS:
        socket.default_value = bulb_on["emission"] * frac
        socket.keyframe_insert("default_value", frame=frame)
        spot.energy = bulb_on["spot"] * frac
        spot.keyframe_insert("energy", frame=frame)
    for owner in (mats["bulb"].node_tree, spot):
        _ease(owner, "LINEAR")


def _animate_camera(camera):
    target = camera.constraints["Track To"].target.location
    start = camera.location.copy()
    end = start.lerp(target, CAMERA_PUSH)
    for frame, loc in ((1, start), (FRAME_END, end)):
        camera.location = loc
        camera.keyframe_insert("location", frame=frame)
    _ease(camera, easing="EASE_IN_OUT")


def setup(rig, mats, studio_objs, bulb_on):
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start, scene.frame_end = 1, FRAME_END
    _animate_rig(rig)
    _animate_studio(studio_objs["lights"])
    _animate_bulb(rig, mats, bulb_on)
    camera = studio_objs["cameras"]["CAM_Anim"]
    _animate_camera(camera)
    scene.camera = camera
    scene.frame_set(1)
