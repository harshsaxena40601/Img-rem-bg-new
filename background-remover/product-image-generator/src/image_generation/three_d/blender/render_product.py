from pathlib import Path
import json
import math

import bpy
import mathutils

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_DIR = (
    PROJECT_ROOT
    / "src"
    / "image_generation"
    / "output"
    / "3d_model"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "src"
    / "image_generation"
    / "blender"
    / "output"
)

RENDER_DIR = (
    OUTPUT_DIR
    / "renders"
)

RESULT_FILE = (
    OUTPUT_DIR
    / "blender_result.json"
)


# ============================================================
# CONFIGURATION
# ============================================================

RENDER_WIDTH = 1024
RENDER_HEIGHT = 1024

MODEL_FILE_NAME = "product_model.glb"


# ============================================================
# CLEAR SCENE
# ============================================================

def clear_scene():
    """
    Remove everything from the default Blender scene.
    """

    bpy.ops.object.select_all(
        action="SELECT"
    )

    bpy.ops.object.delete()

    print("Scene cleared.")


# ============================================================
# FIND MODEL
# ============================================================

def get_model_path():

    model_path = (
        MODEL_DIR
        / MODEL_FILE_NAME
    )

    if not model_path.exists():

        raise FileNotFoundError(
            "\n3D model not found:\n"
            f"{model_path}\n\n"
            "Expected file:\n"
            "product_model.glb"
        )

    return model_path


# ============================================================
# IMPORT GLB
# ============================================================

def import_model(model_path):

    print("\nImporting 3D model...")

    bpy.ops.import_scene.gltf(
        filepath=str(model_path)
    )

    imported_objects = list(
        bpy.context.selected_objects
    )

    if not imported_objects:

        raise RuntimeError(
            "No objects were imported "
            "from the GLB file."
        )

    print(
        f"Imported "
        f"{len(imported_objects)} object(s)."
    )

    return imported_objects


# ============================================================
# CENTER MODEL
# ============================================================

def center_model(objects):

    print("\nCentering model...")

    mesh_objects = [
        obj
        for obj in objects
        if obj.type == "MESH"
    ]

    if not mesh_objects:

        raise RuntimeError(
            "No mesh objects found."
        )

    bpy.ops.object.select_all(
        action="DESELECT"
    )

    for obj in mesh_objects:

        obj.select_set(True)

    bpy.context.view_layer.objects.active = (
        mesh_objects[0]
    )

    bpy.ops.object.origin_set(
        type="ORIGIN_GEOMETRY",
        center="BOUNDS"
    )

    # Calculate combined bounding box.
    min_x = min(
        obj.matrix_world @
        min(obj.bound_box, key=lambda v: v[0])
        for obj in mesh_objects
    )

    # Simpler reliable centering:
    # Create an empty parent for all imported objects.

    bpy.ops.object.empty_add(
        type="PLAIN_AXES",
        location=(0, 0, 0)
    )

    root = bpy.context.active_object
    root.name = "PRODUCT_ROOT"

    for obj in objects:

        obj.parent = root

    # Calculate approximate center
    locations = [
        obj.location.copy()
        for obj in mesh_objects
    ]

    if locations:

        center_x = sum(
            loc.x for loc in locations
        ) / len(locations)

        center_y = sum(
            loc.y for loc in locations
        ) / len(locations)

        center_z = sum(
            loc.z for loc in locations
        ) / len(locations)

        root.location = (
            -center_x,
            -center_y,
            -center_z
        )

    print("Model centered.")

    return root


# ============================================================
# ADD CAMERA
# ============================================================

def create_camera():

    print("\nCreating camera...")

    bpy.ops.object.camera_add(
        location=(0, -5, 1)
    )

    camera = bpy.context.active_object

    camera.name = "PRODUCT_CAMERA"

    bpy.context.scene.camera = camera

    return camera


# ============================================================
# POINT CAMERA
# ============================================================

def point_camera_at(
    camera,
    target=(0, 0, 0)
):

    direction = (
        mathutils.Vector(target)
        - camera.location
    )

    camera.rotation_euler = (
        direction.to_track_quat(
            "-Z",
            "Y"
        ).to_euler()
    )


# ============================================================
# LIGHTING
# ============================================================

def add_area_light(
    name,
    location,
    energy,
    size
):

    bpy.ops.object.light_add(
        type="AREA",
        location=location
    )

    light = bpy.context.active_object

    light.name = name

    light.data.energy = energy

    light.data.shape = "DISK"

    light.data.size = size

    return light


def setup_lighting():

    print("\nSetting up studio lighting...")

    add_area_light(
        name="KEY_LIGHT",
        location=(4, -4, 6),
        energy=1200,
        size=5
    )

    add_area_light(
        name="FILL_LIGHT",
        location=(-4, -2, 3),
        energy=700,
        size=4
    )

    add_area_light(
        name="BACK_LIGHT",
        location=(0, 4, 5),
        energy=1000,
        size=4
    )

    print("Studio lighting created.")


# ============================================================
# WORLD
# ============================================================

def setup_world():

    world = bpy.context.scene.world

    if world:

        world.color = (
            0.05,
            0.05,
            0.05
        )


# ============================================================
# RENDER SETTINGS
# ============================================================

def setup_render_settings():

    scene = bpy.context.scene

    scene.render.engine = "BLENDER_EEVEE_NEXT"

    scene.render.resolution_x = (
        RENDER_WIDTH
    )

    scene.render.resolution_y = (
        RENDER_HEIGHT
    )

    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = (
        "PNG"
    )

    scene.render.film_transparent = False


# ============================================================
# RENDER IMAGE
# ============================================================

def render_view(
    camera,
    name,
    location
):

    print(
        f"\nRendering: {name}"
    )

    camera.location = location

    # Point camera toward product center.
    target = mathutils.Vector(
        (0, 0, 0)
    )

    direction = (
        target
        - camera.location
    )

    camera.rotation_euler = (
        direction
        .to_track_quat(
            "-Z",
            "Y"
        )
        .to_euler()
    )

    output_path = (
        RENDER_DIR
        / f"{name}.png"
    )

    bpy.context.scene.render.filepath = (
        str(output_path)
    )

    bpy.ops.render.render(
        write_still=True
    )

    print(
        f"Saved: {output_path}"
    )

    return str(
        output_path.resolve()
    )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(data):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# MAIN PIPELINE
# ============================================================

def render_product():

    print("\n" + "=" * 60)
    print("BLENDER PRODUCT RENDERING")
    print("=" * 60)

    RENDER_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    clear_scene()

    model_path = get_model_path()

    imported_objects = import_model(
        model_path
    )

    center_model(
        imported_objects
    )

    camera = create_camera()

    setup_lighting()

    setup_world()

    setup_render_settings()

    renders = []

    renders.append(
        render_view(
            camera,
            "front",
            (0, -5, 1)
        )
    )

    renders.append(
        render_view(
            camera,
            "angle_45",
            (4, -4, 2)
        )
    )

    renders.append(
        render_view(
            camera,
            "side",
            (5, 0, 1)
        )
    )

    result = {

        "success": True,

        "model_file": str(
            model_path.resolve()
        ),

        "render_engine": (
            "BLENDER_EEVEE_NEXT"
        ),

        "renders": renders,

        "total_renders": len(
            renders
        )

    }

    save_result(result)

    print("\n" + "=" * 60)
    print("BLENDER RENDERING COMPLETE")
    print("=" * 60)

    for render in renders:

        print(render)

    print(
        f"\nResult:\n{RESULT_FILE}"
    )


if __name__ == "__main__":

    render_product()