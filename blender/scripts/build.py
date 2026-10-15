"""Build the TENSIL scene from scratch and optionally render shots.

Usage:
  blender -b --factory-startup --python blender/scripts/build.py -- \
      [--colorway graphite] [--save blender/tensil_lamp.blend] \
      [--shot NAME:CAMERA:POSE:YAW[:on]] ... [--out renders/test] \
      [--samples 64] [--scale 50] [--override clay|wire]
"""
import argparse
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import animate  # noqa: E402
import lamp  # noqa: E402
import materials  # noqa: E402
import studio  # noqa: E402
from common import collection  # noqa: E402

BULB_ON = {"emission": 30.0, "spot": 28.0}
STUDIO_DIM = 0.18  # studio energy multiplier when the bulb is on


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--colorway", default="graphite", choices=sorted(materials.COLORWAYS))
    p.add_argument("--save")
    p.add_argument("--shot", action="append", default=[])
    p.add_argument("--out", default="renders/test")
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--scale", type=int, default=100)
    p.add_argument("--override", choices=["clay", "wire"])
    p.add_argument("--animate", action="store_true", help="keyframe the product animation")
    p.add_argument("--frames", help="comma list of frames to render as stills, or 'all' for the sequence")
    return p.parse_args(argv)


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def wire_material(clay):
    """Clay with a dark wireframe overlay, for process renders."""
    mat = clay.copy()
    mat.name = "MAT_ClayWire"
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    out = nodes["Material Output"]
    wire = nodes.new("ShaderNodeWireframe")
    wire.use_pixel_size = True
    wire.inputs["Size"].default_value = 1.2
    dark = nodes.new("ShaderNodeBsdfDiffuse")
    dark.inputs["Color"].default_value = (0.02, 0.02, 0.025, 1)
    mix = nodes.new("ShaderNodeMixShader")
    links.new(wire.outputs["Fac"], mix.inputs["Fac"])
    links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    links.new(dark.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], out.inputs["Surface"])
    return mat


def set_bulb(rig, mats, on):
    mats["bulb"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = (
        BULB_ON["emission"] if on else 0.0)
    rig["bulb_light"].data.energy = BULB_ON["spot"] if on else 0.0


def set_studio(studio_objs, energy_mult, lights_visible):
    for name, light in studio_objs["lights"].items():
        light.data.energy = studio.SOFTBOXES[name][2] * energy_mult
        light.visible_camera = lights_visible


def render_shot(spec, rig, mats, studio_objs, out_dir):
    parts = spec.split(":")
    name, cam, pose, yaw = parts[:4]
    on = len(parts) > 4 and parts[4] == "on"
    angles = list(lamp.POSES[pose])
    angles[0] = float(yaw)
    lamp.set_pose(rig, angles)
    set_bulb(rig, mats, on)
    set_studio(studio_objs, STUDIO_DIM if on else 1.0, cam == "CAM_Overview")
    scene = bpy.context.scene
    scene.camera = bpy.data.objects[cam]
    scene.render.filepath = os.path.join(out_dir, f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"[tensil] rendered {scene.render.filepath}")


def main():
    args = parse_args()
    clear_scene()
    mats = materials.build_all(args.colorway)
    rig = lamp.build(mats, collection("Lamp"))
    studio_objs = studio.build(mats, collection("Studio"))
    scene = bpy.context.scene
    scene.cycles.samples = args.samples
    scene.render.resolution_percentage = args.scale
    if args.override:
        layer = scene.view_layers[0]
        layer.material_override = mats["clay"] if args.override == "clay" else wire_material(mats["clay"])
    if args.animate:
        animate.setup(rig, mats, studio_objs, BULB_ON)
    elif args.save:
        lamp.set_pose(rig, "work")
    if args.save:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(args.save))
    for spec in args.shot:
        render_shot(spec, rig, mats, studio_objs, os.path.abspath(args.out))
    if args.frames:
        render_frames(args.frames, os.path.abspath(args.out))


def render_frames(frames, out_dir):
    scene = bpy.context.scene
    if frames == "all":
        scene.render.filepath = os.path.join(out_dir, "frame_")
        bpy.ops.render.render(animation=True)
        return
    for f in (int(x) for x in frames.split(",")):
        scene.frame_set(f)
        scene.render.filepath = os.path.join(out_dir, f"frame_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
        print(f"[tensil] rendered frame {f}")


if __name__ == "__main__":
    main()
