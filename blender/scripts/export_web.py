"""Export the TENSIL lamp (no studio) to GLB for the web.

Spring Stretch-To constraints are not part of glTF, so their evaluated
transforms are baked: as a static pose, or as sampled keys when animated.

Usage:
  blender -b --factory-startup --python blender/scripts/export_web.py -- \
      --out web/tensil_lamp_raw.glb [--animated] [--step 2]
"""
import argparse
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import animate  # noqa: E402
import lamp  # noqa: E402
import materials  # noqa: E402
from common import collection  # noqa: E402


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--animated", action="store_true")
    p.add_argument("--step", type=int, default=2, help="frame step when sampling spring keys")
    return p.parse_args(argv)


def springs():
    return [o for o in bpy.data.objects if o.name.startswith("Spring_")]


def bake_springs(frames):
    """Sample evaluated spring transforms, then drop the constraints."""
    scene = bpy.context.scene
    samples = {o.name: [] for o in springs()}
    for f in frames:
        scene.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        for o in springs():
            world = o.evaluated_get(dg).matrix_world.copy()
            parent = o.parent.evaluated_get(dg).matrix_world.copy()
            samples[o.name].append((f, parent.inverted() @ world))
    for o in springs():
        o.constraints.clear()
        for f, local in samples[o.name]:
            o.matrix_basis = local
            if len(frames) > 1:
                for path in ("location", "rotation_euler", "scale"):
                    o.keyframe_insert(path, frame=f)


def strip_helpers():
    """Remove spring-anchor empties (static export only), keeping children in place."""
    for o in list(bpy.data.objects):
        if o.type == "EMPTY" and o.name.startswith("ANC_"):
            for child in o.children:
                mw = child.matrix_world.copy()
                child.parent = o.parent
                child.matrix_world = mw
            bpy.data.objects.remove(o)


def main():
    args = parse_args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats = materials.build_all("graphite")
    rig = lamp.build(mats, collection("Lamp"))
    bpy.data.objects.remove(rig.pop("bulb_light"))
    scene = bpy.context.scene

    if args.animated:
        scene.render.fps = animate.FPS
        scene.frame_start, scene.frame_end = 1, animate.FRAME_END
        animate._animate_rig(rig)
        frames = list(range(1, animate.FRAME_END + 1, args.step)) + [animate.FRAME_END]
    else:
        lamp.set_pose(rig, "work")
        frames = [scene.frame_current]
    bake_springs(frames)
    if not args.animated:
        bpy.context.view_layer.update()
        strip_helpers()

    out = os.path.abspath(args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=out,
        export_format="GLB",
        export_apply=True,
        export_animations=args.animated,
        export_animation_mode="SCENE",
        export_anim_scene_split_object=False,
        export_lights=False,
        export_cameras=False,
        export_yup=True,
    )
    dg = bpy.context.evaluated_depsgraph_get()
    tris = sum(len(p.vertices) - 2 for o in scene.objects if o.type == "MESH"
               for p in o.evaluated_get(dg).data.polygons)
    print(f"[tensil] exported {out} ({os.path.getsize(out) / 1024:.0f} KiB, ~{tris} triangles)")


if __name__ == "__main__":
    main()
