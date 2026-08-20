from pathlib import Path
import json


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


PRODUCT_PROFILE_FILE = (
    PROJECT_ROOT
    / "output"
    / "product_profile"
    / "product_profile.json"
)


REFERENCE_IMAGES_DIR = (
    PROJECT_ROOT
    / "input"
    / "reference_images"
)


OUTPUT_DIR = (
    PROJECT_ROOT
    / "output"
    / "img_generation"
)


OUTPUT_FILE = (
    OUTPUT_DIR
    / "3d_generation_input.json"
)


# ============================================================
# JSON HELPERS
# ============================================================

def load_json(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"\nFile not found:\n{file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_json(data):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
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
# REFERENCE IMAGE DETECTION
# ============================================================

def get_image_view(filename):

    name = filename.lower()

    if any(
        word in name
        for word in [
            "front",
            "main",
            "primary"
        ]
    ):
        return "front"

    if any(
        word in name
        for word in [
            "back",
            "rear"
        ]
    ):
        return "back"

    if any(
        word in name
        for word in [
            "side",
            "left",
            "right"
        ]
    ):
        return "side"

    if any(
        word in name
        for word in [
            "detail",
            "close",
            "texture",
            "hardware"
        ]
    ):
        return "detail"

    if any(
        word in name
        for word in [
            "lifestyle",
            "model",
            "person",
            "usage"
        ]
    ):
        return "lifestyle"

    return "unknown"


def get_image_purpose(view):

    purposes = {

        "front": [
            "overall shape",
            "main proportions",
            "front design"
        ],

        "back": [
            "rear structure",
            "overall proportions"
        ],

        "side": [
            "depth",
            "side geometry",
            "volume"
        ],

        "detail": [
            "material texture",
            "hardware details",
            "small product features"
        ],

        "lifestyle": [
            "real world scale",
            "usage proportions"
        ],

        "unknown": [
            "additional visual reference"
        ]
    }

    return purposes.get(
        view,
        purposes["unknown"]
    )


def find_reference_images():

    if not REFERENCE_IMAGES_DIR.exists():

        raise FileNotFoundError(
            "\nReference images folder not found:\n"
            f"{REFERENCE_IMAGES_DIR}"
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    images = []

    for file in REFERENCE_IMAGES_DIR.iterdir():

        if (
            file.is_file()
            and file.suffix.lower()
            in allowed_extensions
        ):

            view = get_image_view(
                file.name
            )

            images.append(
                {
                    "filename": file.name,

                    "path": str(
                        file.relative_to(
                            PROJECT_ROOT
                        )
                    ),

                    "view": view,

                    "use_for": get_image_purpose(
                        view
                    )
                }
            )

    if not images:

        raise FileNotFoundError(
            "\nNo reference images found in:\n"
            f"{REFERENCE_IMAGES_DIR}"
        )

    return images


# ============================================================
# PRODUCT DATA EXTRACTION
# ============================================================

def extract_product_data(profile):

    return profile.get(
        "product",
        {}
    )


def build_geometry(product):

    return {

        "category": product.get(
            "category"
        ),

        "overall_shape": product.get(
            "shape"
        ),

        "size_clues": product.get(
            "size_clues"
        ),

        "handles_or_straps": product.get(
            "handles_or_straps"
        )
    }


def build_materials(product):

    return {

        "primary_material": product.get(
            "material"
        ),

        "texture": product.get(
            "texture"
        ),

        "primary_color": product.get(
            "primary_color"
        ),

        "secondary_colors": product.get(
            "secondary_colors",
            []
        )
    }


def build_hardware(product):

    return {

        "description": product.get(
            "hardware"
        )
    }


# ============================================================
# BUILD 3D GENERATION INPUT
# ============================================================

def build_3d_generation_input():

    print("\n" + "=" * 60)
    print("3D GENERATION INPUT PREPARATION")
    print("=" * 60)

    print(
        "\nLoading product profile..."
    )

    profile = load_json(
        PRODUCT_PROFILE_FILE
    )

    product = extract_product_data(
        profile
    )

    print(
        "Scanning reference images..."
    )

    reference_images = (
        find_reference_images()
    )

    print(
        f"Reference images found: "
        f"{len(reference_images)}"
    )

    generation_input = {

        "product": {

            "name": product.get(
                "name"
            ),

            "brand": product.get(
                "brand"
            ),

            "category": product.get(
                "category"
            )
        },

        "geometry": build_geometry(
            product
        ),

        "materials": build_materials(
            product
        ),

        "hardware": build_hardware(
            product
        ),

        "distinctive_features": profile.get(
            "distinctive_features",
            []
        ),

        "reference_images": reference_images,

        "generation_requirements": {

            "model_type":
                "realistic 3D product model",

            "target_format":
                "glb",

            "preserve_product_identity":
                True,

            "preserve_overall_shape":
                True,

            "preserve_proportions":
                True,

            "preserve_material_details":
                True,

            "preserve_texture":
                True,

            "preserve_hardware_details":
                True,

            "generate_texture_maps":
                True,

            "target_quality":
                "high"
        },

        "source_information": {

            "product_profile":
                str(
                    PRODUCT_PROFILE_FILE.relative_to(
                        PROJECT_ROOT
                    )
                ),

            "verified_match":
                profile.get(
                    "verified_match",
                    {}
                ),

            "matched_product":
                profile.get(
                    "matched_product",
                    {}
                )
        }
    }

    return generation_input


# ============================================================
# MAIN
# ============================================================

def main():

    generation_input = (
        build_3d_generation_input()
    )

    save_json(
        generation_input
    )

    print("\n" + "=" * 60)
    print("3D INPUT CREATED")
    print("=" * 60)

    print(
        "\nSaved:"
    )

    print(
        OUTPUT_FILE
    )

    print(
        "\nProduct:"
    )

    print(
        generation_input["product"]["name"]
    )

    print(
        "\nReference Images:"
    )

    for image in generation_input[
        "reference_images"
    ]:

        print(
            f"\n- {image['filename']}"
        )

        print(
            f"  View: {image['view']}"
        )

    return generation_input


if __name__ == "__main__":
    main()