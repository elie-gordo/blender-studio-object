"""Post-processing with Blender only (no system FFmpeg needed).

Usage:
  blender -b --factory-startup --python blender/scripts/postprocess.py -- video FRAMES_DIR OUT.mp4 [FPS]
  blender -b --factory-startup --python blender/scripts/postprocess.py -- webp OUT_DIR WIDTH IMG.png [IMG.png ...]
"""
import os
import sys

import bpy


def encode_video(frames_dir, out_path, fps=30):
    frames = sorted(f for f in os.listdir(frames_dir) if f.lower().endswith(".png"))
    if not frames:
        raise SystemExit(f"no PNG frames in {frames_dir}")
    scene = bpy.context.scene
    editor = scene.sequence_editor_create()
    strips = editor.strips if hasattr(editor, "strips") else editor.sequences
    strip = strips.new_image("frames", os.path.join(frames_dir, frames[0]), 1, 1)
    for name in frames[1:]:
        strip.elements.append(name)
    first = bpy.data.images.load(os.path.join(frames_dir, frames[0]))
    scene.render.resolution_x, scene.render.resolution_y = first.size
    scene.render.resolution_percentage = 100
    scene.render.fps = fps
    scene.frame_start, scene.frame_end = 1, len(frames)
    settings = scene.render.image_settings
    if hasattr(settings, "media_type"):
        settings.media_type = "VIDEO"
    settings.file_format = "FFMPEG"
    ff = scene.render.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"
    ff.constant_rate_factor = "HIGH"
    ff.ffmpeg_preset = "GOOD"
    ff.audio_codec = "NONE"
    scene.render.filepath = os.path.abspath(out_path)
    bpy.ops.render.render(animation=True)
    print(f"[tensil] video {out_path} ({len(frames)} frames @ {fps} fps)")


def to_webp(out_dir, width, paths, quality=85):
    os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    settings = scene.render.image_settings
    if hasattr(settings, "media_type"):
        settings.media_type = "IMAGE"
    settings.file_format = "WEBP"
    settings.quality = quality
    settings.color_mode = "RGB"
    # Sources are already display-referred PNGs: don't apply AgX a second time.
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    for path in paths:
        img = bpy.data.images.load(os.path.abspath(path))
        w, h = img.size
        if w > width:
            img.scale(width, round(h * width / w))
        out = os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + ".webp")
        img.save_render(out, scene=scene)
        print(f"[tensil] webp {out} {img.size[0]}x{img.size[1]}")


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    mode = args[0]
    if mode == "video":
        encode_video(args[1], args[2], int(args[3]) if len(args) > 3 else 30)
    elif mode == "webp":
        to_webp(args[1], int(args[2]), args[3:])
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
