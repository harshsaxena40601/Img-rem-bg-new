from pathlib import Path
import os

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load .env
load_dotenv(PROJECT_ROOT / ".env")


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
)


# Product folder
PRODUCTS_DIR = PROJECT_ROOT / "input" / "products"


def find_product_image():
    """Find the first supported image in input/products."""

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
        raise FileNotFoundError(
            f"No supported image found in: {PRODUCTS_DIR}"
        )

    return images[0]


def upload_product_image(image_path):
    """Upload the product image to Cloudinary."""

    print("\nUploading image to Cloudinary...")

    result = cloudinary.uploader.upload(
        str(image_path),
        folder="product-image-generator/products",
        resource_type="image",
    )

    return result


def main():

    print("\n" + "=" * 50)
    print("PRODUCT IMAGE UPLOAD")
    print("=" * 50)

    image_path = find_product_image()

    print(f"\nImage found: {image_path.name}")

    result = upload_product_image(image_path)

    print("\nUpload successful.")

    print("\n" + "=" * 50)
    print("CLOUDINARY RESULT")
    print("=" * 50)

    print(f"\nPublic ID: {result['public_id']}")
    print(f"Image URL: {result['secure_url']}")


if __name__ == "__main__":
    main()