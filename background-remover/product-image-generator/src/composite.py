from pathlib import Path
from PIL import Image


PROJECT_DIR = Path(__file__).resolve().parent.parent

PRODUCT_DIR = PROJECT_DIR / "input" / "product"
SCENE_DIR = PROJECT_DIR / "input" / "scenes"
OUTPUT_DIR = PROJECT_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


def get_first_image(folder):
    extensions = {".png", ".jpg", ".jpeg", ".webp"}

    images = [
        file
        for file in folder.iterdir()
        if file.suffix.lower() in extensions
    ]

    if not images:
        raise FileNotFoundError(
            f"No supported image found in: {folder}"
        )

    return images[0]


def composite_product(
    scene_path,
    product_path,
    output_path,
    scale=0.35,
    x_ratio=0.5,
    y_ratio=0.5,
):
    scene = Image.open(scene_path).convert("RGBA")
    product = Image.open(product_path).convert("RGBA")

    scene_width, scene_height = scene.size
    product_width, product_height = product.size

    # Resize product relative to scene width
    new_width = int(scene_width * scale)

    new_height = int(
        product_height * new_width / product_width
    )

    product = product.resize(
        (new_width, new_height),
        Image.Resampling.LANCZOS
    )

    # Position product using ratios
    x = int(
        scene_width * x_ratio
        - new_width / 2
    )

    y = int(
        scene_height * y_ratio
        - new_height / 2
    )

    # Create result
    result = scene.copy()

    result.alpha_composite(
        product,
        (x, y)
    )

    result.save(
        output_path,
        "PNG"
    )

    print("\nCOMPOSITE COMPLETE")
    print(f"Scene:   {scene_path.name}")
    print(f"Product: {product_path.name}")
    print(f"Position: {x}, {y}")
    print(f"Product size: {new_width} x {new_height}")
    print(f"Output:  {output_path}")


if __name__ == "__main__":

    scene_path = get_first_image(SCENE_DIR)
    product_path = get_first_image(PRODUCT_DIR)

    output_path = (
        OUTPUT_DIR / "first_composite.png"
    )

    composite_product(
        scene_path=scene_path,
        product_path=product_path,
        output_path=output_path,

        # Change these values to move the product
        scale=0.35,
        x_ratio=0.5,
        y_ratio=0.6,
    )