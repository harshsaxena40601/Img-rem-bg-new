from pathlib import Path
import numpy as np

from device_info import print_device_info
from remover import BackgroundRemover
from estimator import (
    calibrate_pipeline,
    estimate_total_time,
    format_time
)
from image_analyzer import (
    analyze_images,
    print_image_analysis
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "onnx"
    / "model_fp16.onnx"
)

MODEL_TYPE = "modnet"
DEVICE = "CPU"


def get_images():
    supported_formats = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".avif"
    }

    return [
        file
        for file in INPUT_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in supported_formats
    ]


def create_benchmark_input():
    """
    MODNet uses 512x512 RGB input.
    Shape: [1, 3, 512, 512]
    """

    return np.random.rand(
        1,
        3,
        512,
        512
    ).astype(np.float32)


def main():
    print_device_info()

    images = get_images()

    if not images:
        print("\nNo supported images found.")
        return

    print("\n" + "=" * 50)
    print("BACKGROUND REMOVAL")
    print("=" * 50)

    print(f"\nFound {len(images)} image(s).")

    image_analysis = analyze_images(images)

    print_image_analysis(image_analysis)

    remover = BackgroundRemover(
        model_path=str(MODEL_PATH),
        device=DEVICE,
        model_type=MODEL_TYPE
    )

    # -----------------------------------------
    # PERFORMANCE BENCHMARK
    # -----------------------------------------

    calibration = calibrate_pipeline(
        remover,
        images[0],
        runs=3
    )

    estimate = estimate_total_time(
        calibration,
        len(images)
    )

    print("\n" + "=" * 50)
    print("PERFORMANCE ESTIMATE")
    print("=" * 50)

    print(f"\nModel: {MODEL_TYPE}")
    print(f"Device: {DEVICE}")

    print(
        f"\nPreprocessing: "
        f"{format_time(calibration['preprocess'])}"
    )

    print(
        f"Inference: "
        f"{format_time(calibration['inference'])}"
    )

    print(
        f"Postprocessing: "
        f"{format_time(calibration['postprocess'])}"
    )

    print(
        f"PNG saving: "
        f"{format_time(calibration['save'])}"
    )

    print(
        f"\nEstimated per image: "
        f"{format_time(estimate['estimated_per_image'])}"
    )

    print(
        f"Estimated total time: "
        f"{format_time(estimate['estimated_total'])}"
    )

    print("\nStarting processing...")

    # -----------------------------------------
    # PROCESS IMAGES
    # -----------------------------------------

    actual_total_start = __import__("time").perf_counter()

    for image_path in images:

        print("\n" + "-" * 50)
        print(f"Processing: {image_path.name}")

        result = remover.remove(image_path)

        output_path = (
            OUTPUT_DIR
            / f"{image_path.stem}_removed.png"
        )

        save_time = remover.save(
            result,
            output_path
        )

        total_time = (
            result["total_time"]
            + save_time
        )

        print("Done.")

        print(
            f"Actual time: "
            f"{format_time(total_time)}"
        )

        print(
            f"Output: {output_path.name}"
        )

    actual_total_time = (
        __import__("time").perf_counter()
        - actual_total_start
    )

    print("\n" + "=" * 50)
    print("ALL IMAGES PROCESSED")
    print("=" * 50)

    print(
        f"\nEstimated total: "
        f"{format_time(estimate['estimated_total'])}"
    )

    print(
        f"Actual total:    "
        f"{format_time(actual_total_time)}"
    )


if __name__ == "__main__":
    main()