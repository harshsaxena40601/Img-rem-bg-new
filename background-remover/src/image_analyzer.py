from pathlib import Path
from PIL import Image


def analyze_image(image_path):
    image_path = Path(image_path)

    with Image.open(image_path) as image:
        width, height = image.size
        image_format = image.format
        mode = image.mode

    file_size_bytes = image_path.stat().st_size

    megapixels = (
        width * height
    ) / 1_000_000

    return {
        "path": image_path,
        "name": image_path.name,
        "format": image_format,
        "mode": mode,
        "width": width,
        "height": height,
        "megapixels": megapixels,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": (
            file_size_bytes / (1024 * 1024)
        ),
    }


def analyze_images(image_paths):
    return [
        analyze_image(image_path)
        for image_path in image_paths
    ]


def print_image_analysis(images):
    print("\n" + "=" * 50)
    print("INPUT IMAGE ANALYSIS")
    print("=" * 50)

    for image in images:
        print(f"\nName: {image['name']}")
        print(f"Format: {image['format']}")
        print(
            f"Dimensions: "
            f"{image['width']} x {image['height']}"
        )
        print(
            f"Megapixels: "
            f"{image['megapixels']:.2f} MP"
        )
        print(
            f"File size: "
            f"{image['file_size_mb']:.2f} MB"
        )