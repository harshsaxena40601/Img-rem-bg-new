import json
from pathlib import Path
from datetime import datetime


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
IMAGES_DIR = INPUT_DIR / "images"

PRODUCT_DATA_FILE = INPUT_DIR / "product_data.json"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = OUTPUT_DIR / "product_spec.json"


# ============================================================
# LOAD PRODUCT DATA
# ============================================================

def load_product_data():
    print("\nLoading product data...")

    if not PRODUCT_DATA_FILE.exists():
        raise FileNotFoundError(
            f"product_data.json not found:\n{PRODUCT_DATA_FILE}"
        )

    with open(PRODUCT_DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


# ============================================================
# FIND PRODUCT IMAGES
# ============================================================

def find_product_images():
    print("Scanning product images...")

    if not IMAGES_DIR.exists():
        raise FileNotFoundError(
            f"Images folder not found:\n{IMAGES_DIR}"
        )

    supported_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    images = []

    for file in sorted(IMAGES_DIR.iterdir()):

        if (
            file.is_file()
            and file.suffix.lower() in supported_extensions
        ):
            images.append({
                "filename": file.name,
                "path": str(file.resolve()),
                "extension": file.suffix.lower()
            })

    if not images:
        raise ValueError(
            "No supported images found in input/images/"
        )

    print(f"Found {len(images)} image(s).")

    return images


# ============================================================
# BUILD PRODUCT SPECIFICATION
# ============================================================

def build_product_spec(product_data, images):

    product_spec = {

        "metadata": {
            "created_at": datetime.now().isoformat(),
            "source": "temporary_manual_input",
            "pipeline_stage": "product_specification"
        },

        "product": {
            "name": product_data.get("product_name"),
            "category": product_data.get("category"),
            "brand": product_data.get("brand"),
            "description": product_data.get("description")
        },

        "physical_properties": {
            "material": product_data.get("material"),
            "color": product_data.get("color"),
            "shape": product_data.get("shape"),
            "features": product_data.get("features")
        },

        "reference_images": {
            "count": len(images),
            "images": images
        },

        "generation_goal": product_data.get(
            "generation_goal",
            {}
        )

    }

    return product_spec


# ============================================================
# SAVE PRODUCT SPEC
# ============================================================

def save_product_spec(product_spec):

    print("\nSaving product specification...")

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
            product_spec,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("Product specification created successfully.")
    print(f"\nOutput:\n{OUTPUT_FILE}")


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("PRODUCT SPEC BUILDER")
    print("=" * 60)

    try:

        product_data = load_product_data()

        images = find_product_images()

        product_spec = build_product_spec(
            product_data,
            images
        )

        save_product_spec(
            product_spec
        )

        print("\n" + "=" * 60)
        print("DONE")
        print("=" * 60)

    except Exception as error:

        print("\nERROR:")
        print(error)


if __name__ == "__main__":
    main()