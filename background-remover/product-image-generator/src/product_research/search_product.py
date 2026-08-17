from pathlib import Path
from PIL import Image


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Product input folder
PRODUCTS_DIR = PROJECT_ROOT / "input" / "products"


def find_product_image():
    """Find the first supported product image."""

    supported_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    images = [
        file
        for file in PRODUCTS_DIR.iterdir()
        if file.suffix.lower() in supported_extensions
    ]

    if not images:
        print("ERROR: No product image found.")
        return None

    return images[0]


def analyze_image(image_path):
    """Print basic information about the product image."""

    with Image.open(image_path) as image:
        width, height = image.size
        image_format = image.format

    file_size_mb = image_path.stat().st_size / (1024 * 1024)

    print("\n" + "=" * 50)
    print("PRODUCT IMAGE DETECTED")
    print("=" * 50)

    print(f"\nFile:       {image_path.name}")
    print(f"Path:       {image_path}")
    print(f"Format:     {image_format}")
    print(f"Dimensions: {width} x {height}")
    print(f"File size:  {file_size_mb:.2f} MB")


def main():

    print("\n" + "=" * 50)
    print("PRODUCT RESEARCH PIPELINE")
    print("=" * 50)

    image_path = find_product_image()

    if image_path is None:
        return

    analyze_image(image_path)

    print("\nProduct image is ready for visual search.")


if __name__ == "__main__":
    main()