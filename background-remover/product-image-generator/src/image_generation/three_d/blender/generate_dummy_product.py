from pathlib import Path
import json

import bpy


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

BLENDER_DIR = (
    PROJECT_ROOT
    / "src"
    / "image_generation"
    / "three_d"
    / "blender"
)

INPUT_FILE = (
    BLENDER_DIR
    / "dummy_product.json"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "src"
    / "image_generation"
    / "output"
    / "3d_model"
)

BLEND_FILE = (
    OUTPUT_DIR
    / "product_model.blend"
)

GLB_FILE = (
    OUTPUT_DIR
    / "product_model.glb"
)


# ============================================================
# CLEAR SCENE
# ============================================================

def clear_scene():

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete()

    print("Scene cleared.")


# ============================================================
# LOAD PRODUCT DATA
# ============================================================

def load_product_data():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Dummy product file not found:\n"
            f"{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    print(
        f"Loaded product: "
        f"{data['product']['name']}"
    )

    return data


# ============================================================
# CREATE MATERIAL
# ============================================================

def create_material(material_data):

    material = bpy.data.materials.new(
        name=material_data["name"]
    )

    material.use_nodes = True

    bsdf = (
        material
        .node_tree
        .nodes
        .get("Principled BSDF")
    )

    if bsdf:

        bsdf.inputs[
            "Base Color"
        ].default_value = (
            material_data["color"]
        )

        bsdf.inputs[
            "Metallic"
        ].default_value = (
            material_data["metallic"]
        )

        bsdf.inputs[
            "Roughness"
        ].default_value = (
            material_data["roughness"]
        )

    return material


# ============================================================
# CREATE BAG BODY
# ============================================================

def create_bag_body(
    dimensions,
    body_data,
    material
):

    width = dimensions["width"]
    height = dimensions["height"]
    depth = dimensions["depth"]

    print(
        f"Creating body: "
        f"{width} x {height} x {depth}"
    )

    bpy.ops.mesh.primitive_cube_add(
        location=(
            0,
            0,
            height / 2
        )
    )

    bag_body = bpy.context.active_object

    bag_body.name = "BAG_BODY"

    bag_body.dimensions = (
        width,
        depth,
        height
    )

    # Apply scale so bevel works correctly.
    bpy.ops.object.transform_apply(
        location=False,
        rotation=False,
        scale=True
    )

    corner_radius = (
        body_data["corner_radius"]
    )

    bevel = bag_body.modifiers.new(
        name="Rounded_Corners",
        type="BEVEL"
    )

    bevel.width = corner_radius

    bevel.segments = 6

    # Smooth shading
    bpy.ops.object.shade_smooth()

    # Add material
    bag_body.data.materials.append(
        material
    )

    return bag_body


# ============================================================
# CREATE HANDLE
# ============================================================

def create_handle(
    dimensions,
    handle_data,
    material
):

    if not handle_data["enabled"]:

        print("Handle disabled.")

        return None

    bag_height = dimensions["height"]

    handle_width = handle_data["width"]

    handle_height = handle_data["height"]

    thickness = handle_data["thickness"]

    print("Creating handle...")

    # Create a Bezier curve.
    bpy.ops.curve.primitive_bezier_curve_add()

    handle = bpy.context.active_object

    handle.name = "BAG_HANDLE"

    handle.data.dimensions = "3D"

    handle.data.bevel_depth = thickness

    handle.data.bevel_resolution = 5

    # Position handle above bag.
    handle.location = (
        0,
        0,
        bag_height
    )

    # Scale the default curve.
    handle.scale = (
        handle_width / 2,
        handle_height,
        1
    )

    # Rotate so it forms an arch
    handle.rotation_euler = (
        1.5708,
        0,
        0
    )

    handle.data.materials.append(
        material
    )

    return handle


# ============================================================
# EXPORT MODEL
# ============================================================

def export_model():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nSaving Blender file...")

    bpy.ops.wm.save_as_mainfile(
        filepath=str(BLEND_FILE)
    )

    print(
        f"Saved: {BLEND_FILE}"
    )

    print("\nExporting GLB...")

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.export_scene.gltf(
        filepath=str(GLB_FILE),
        export_format="GLB",
        use_selection=True
    )

    print(
        f"Exported: {GLB_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def generate_product():

    print("\n" + "=" * 60)

    print("DUMMY BLENDER PRODUCT GENERATION")

    print("=" * 60)

    clear_scene()

    product_data = load_product_data()

    dimensions = (
        product_data["dimensions"]
    )

    body_data = (
        product_data["body"]
    )

    handle_data = (
        product_data["handle"]
    )

    material_data = (
        product_data["material"]
    )

    material = create_material(
        material_data
    )

    create_bag_body(
        dimensions,
        body_data,
        material
    )

    create_handle(
        dimensions,
        handle_data,
        material
    )

    export_model()

    print("\n" + "=" * 60)

    print("PRODUCT GENERATION COMPLETE")

    print("=" * 60)


if __name__ == "__main__":

    generate_product()