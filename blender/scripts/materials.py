"""Procedural PBR materials for TENSIL (no external textures)."""
import bpy

# Lacquer colorways (linear RGB). Final choice is made by the art director.
COLORWAYS = {
    "graphite": (0.035, 0.038, 0.042),
    "sage": (0.16, 0.22, 0.17),
    "oxide": (0.42, 0.075, 0.035),
    "cream": (0.78, 0.72, 0.60),
}
BULB_COLOR = (1.0, 0.72, 0.42)  # ~2700 K warm white


def _principled(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    return mat, bsdf


def lacquer(colorway):
    mat, bsdf = _principled("MAT_Lacquer")
    bsdf.inputs["Base Color"].default_value = (*COLORWAYS[colorway], 1)
    bsdf.inputs["Roughness"].default_value = 0.38
    bsdf.inputs["Coat Weight"].default_value = 0.6
    bsdf.inputs["Coat Roughness"].default_value = 0.12
    return mat


def brushed_metal(name="MAT_BrushedSteel", tint=(0.80, 0.80, 0.80), base_rough=0.28):
    """Metal with stretched-noise roughness to read as brushed without UVs."""
    mat, bsdf = _principled(name)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf.inputs["Base Color"].default_value = (*tint, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    coord = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (600, 600, 4)
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1.0
    noise.inputs["Detail"].default_value = 4.0
    ramp = nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = base_rough - 0.08
    ramp.inputs["To Max"].default_value = base_rough + 0.08
    links.new(coord.outputs["Object"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    links.new(ramp.outputs["Result"], bsdf.inputs["Roughness"])
    return mat


def polished_steel():
    mat, bsdf = _principled("MAT_SpringSteel")
    bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.76, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.16
    return mat


def rubber():
    mat, bsdf = _principled("MAT_Rubber")
    bsdf.inputs["Base Color"].default_value = (0.015, 0.015, 0.016, 1)
    bsdf.inputs["Roughness"].default_value = 0.75
    return mat


def reflector():
    mat, bsdf = _principled("MAT_Reflector")
    bsdf.inputs["Base Color"].default_value = (0.85, 0.84, 0.82, 1)
    bsdf.inputs["Roughness"].default_value = 0.45
    return mat


def bulb():
    """Frosted bulb; `Emission Strength` is keyframed by the animation."""
    mat, bsdf = _principled("MAT_Bulb")
    bsdf.inputs["Base Color"].default_value = (0.95, 0.93, 0.90, 1)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Transmission Weight"].default_value = 0.3
    bsdf.inputs["Emission Color"].default_value = (*BULB_COLOR, 1)
    bsdf.inputs["Emission Strength"].default_value = 0.0
    return mat


def backdrop():
    mat, bsdf = _principled("MAT_Backdrop")
    bsdf.inputs["Base Color"].default_value = (0.42, 0.41, 0.39, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    return mat


def clay():
    mat, bsdf = _principled("MAT_Clay")
    bsdf.inputs["Base Color"].default_value = (0.55, 0.55, 0.55, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    return mat


def build_all(colorway="graphite"):
    return {
        "lacquer": lacquer(colorway),
        "metal": brushed_metal(),
        "brass": brushed_metal("MAT_BrushedBrass", tint=(0.80, 0.56, 0.30), base_rough=0.32),
        "spring": polished_steel(),
        "rubber": rubber(),
        "reflector": reflector(),
        "bulb": bulb(),
        "backdrop": backdrop(),
        "clay": clay(),
    }
