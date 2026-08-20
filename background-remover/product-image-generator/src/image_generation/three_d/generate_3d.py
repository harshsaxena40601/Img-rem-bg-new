from pathlib import Path
import json

from providers.base_3d_provider import Base3DProvider


PROJECT_ROOT = Path(__file__).resolve().parents[3]

IMAGE_GENERATION_DIR = (
    PROJECT_ROOT
    / "src"
    / "image_generation"
)

REQUEST_FILE = (
    IMAGE_GENERATION_DIR
    / "output"
    / "3d_request.json"
)

OUTPUT_DIR = (
    IMAGE_GENERATION_DIR
    / "output"
    / "3d_model"
)

RESULT_FILE = (
    OUTPUT_DIR
    / "generation_result.json"
)


def load_3d_request():
    """
    Load the prepared 3D request.
    """

    if not REQUEST_FILE.exists():
        raise FileNotFoundError(
            f"3D request file not found:\n{REQUEST_FILE}"
        )

    with open(
        REQUEST_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def validate_reference_images(request_data):
    """
    Validate that all reference images
    mentioned in the request actually exist.
    """

    reference_images = request_data.get(
        "reference_images",
        []
    )

    if not reference_images:
        raise ValueError(
            "No reference images found in 3d_request.json"
        )

    valid_images = []

    print("\nValidating reference images...")

    for image_path in reference_images:

        path = Path(image_path)

        if path.exists():

            valid_images.append(
                str(path.resolve())
            )

            print(
                f"✓ Found: {path.name}"
            )

        else:

            print(
                f"✗ Missing: {path}"
            )

    if not valid_images:
        raise FileNotFoundError(
            "None of the reference images exist."
        )

    return valid_images


class Dummy3DProvider(Base3DProvider):
    """
    Temporary provider.

    This does NOT generate a real 3D model.

    It allows us to test the complete
    pipeline architecture before connecting
    a real Image-to-3D model.
    """

    def generate(
        self,
        request_data: dict,
        output_dir: Path,
    ) -> dict:

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "\nRunning Dummy 3D Provider..."
        )

        print(
            "This is a pipeline test only."
        )

        print(
            "\nProduct:"
        )

        product_name = (
            request_data
            .get("product", {})
            .get("name")
        )

        print(product_name)

        reference_images = request_data.get(
            "reference_images",
            []
        )

        print(
            f"\nReference images received: "
            f"{len(reference_images)}"
        )

        return {

            "success": True,

            "provider": "dummy",

            "status": "pipeline_test_complete",

            "message": (
                "3D generation architecture "
                "is working correctly. "
                "No real 3D model was generated."
            ),

            "reference_images_used": (
                reference_images
            ),

            "model_file": None,

            "textures": [],

        }


def save_result(result):

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
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "\nGeneration result saved:"
    )

    print(RESULT_FILE)


def generate_3d():

    print("\n" + "=" * 60)

    print("3D MODEL GENERATION")

    print("=" * 60)

    print(
        "\nLoading 3D request..."
    )

    request_data = load_3d_request()

    reference_images = (
        validate_reference_images(
            request_data
        )
    )

    # Replace the image list with
    # validated absolute paths.
    request_data[
        "reference_images"
    ] = reference_images

    print(
        f"\nValid reference images: "
        f"{len(reference_images)}"
    )

    print(
        "\nSelecting 3D provider..."
    )

    provider = Dummy3DProvider()

    result = provider.generate(
        request_data=request_data,
        output_dir=OUTPUT_DIR,
    )

    save_result(result)

    print("\n" + "=" * 60)

    print("3D GENERATION STEP COMPLETE")

    print("=" * 60)

    print(
        "\nProvider:"
        f" {result.get('provider')}"
    )

    print(
        "Status:"
        f" {result.get('status')}"
    )

    print(
        f"\nOutput directory:\n"
        f"{OUTPUT_DIR}"
    )

    return result


def main():

    return generate_3d()


if __name__ == "__main__":

    main()