from pathlib import Path
import json


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = (
    BASE_DIR
    / "output"
    / "product_spec.json"
)

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "3d_request.json"
)


# ============================================================
# LOAD PRODUCT SPEC
# ============================================================

def load_product_spec():

    print("\nLoading product specification...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Product specification not found:\n{INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# EXTRACT REFERENCE IMAGES
# ============================================================

def get_reference_images(product_spec):

    reference_data = product_spec.get(
        "reference_images",
        {}
    )

    images = reference_data.get(
        "images",
        []
    )

    return [
        image.get("path")
        for image in images
        if image.get("path")
    ]


# ============================================================
# BUILD 3D REQUEST
# ============================================================

def build_3d_request(product_spec):

    product = product_spec.get(
        "product",
        {}
    )

    physical_properties = product_spec.get(
        "physical_properties",
        {}
    )

    material = physical_properties.get(
        "material",
        {}
    )

    color = physical_properties.get(
        "color",
        {}
    )

    shape = physical_properties.get(
        "shape",
        {}
    )

    features = physical_properties.get(
        "features",
        []
    )

    reference_images = get_reference_images(
        product_spec
    )

    request = {

        "task": "generate_3d_product",

        "product": {

            "name": product.get("name"),

            "category": product.get("category"),

            "brand": product.get("brand"),

            "description": product.get(
                "description"
            ),
        },

        "geometry": {

            "shape": shape,

            "required_features": features,

            "preserve_proportions": True,

            "preserve_product_identity": True,
        },

        "materials": material,

        "colors": color,

        "reference_images": reference_images,

        "reference_image_count": len(
            reference_images
        ),

        "generation_requirements": {

            "asset_type": "3d_model",

            "preferred_formats": [
                "glb",
                "obj",
            ],

            "require_textures": True,

            "require_materials": True,

            "require_multiple_views": True,

            "preserve_shape": True,

            "preserve_material": True,

            "preserve_colors": True,

            "preserve_distinctive_features": True,
        },

        "output": {

            "directory": str(
                BASE_DIR / "output" / "generated_3d"
            )
        }
    }

    return request


# ============================================================
# SAVE 3D REQUEST
# ============================================================

def save_3d_request(request):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            request,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n3D request created.")

    print(
        f"\nSaved:\n{OUTPUT_FILE}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("3D REQUEST PREPARATION")
    print("=" * 60)

    product_spec = load_product_spec()

    request = build_3d_request(
        product_spec
    )

    save_3d_request(request)

    print("\n" + "=" * 60)
    print("3D REQUEST READY")
    print("=" * 60)

    print(
        f"\nReference images: "
        f"{request['reference_image_count']}"
    )

    print(
        f"Product: "
        f"{request['product']['name']}"
    )

    return request


if __name__ == "__main__":
    main()