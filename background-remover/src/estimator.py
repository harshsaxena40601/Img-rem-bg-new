import time
from pathlib import Path
import tempfile

from PIL import Image


def benchmark_remover(remover, input_data, runs=5):
    """Benchmark inference speed on the current PC."""

    print("\nRunning inference performance test...")

    # Warm-up
    remover.infer_request.infer(
        {
            remover.input_layer: input_data
        }
    )

    times = []

    for _ in range(runs):
        start = time.perf_counter()

        remover.infer_request.infer(
            {
                remover.input_layer: input_data
            }
        )

        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        "runs": runs,
        "average_inference_time": sum(times) / len(times),
        "min_inference_time": min(times),
        "max_inference_time": max(times),
    }


def calibrate_pipeline(remover, sample_image_path, runs=3):
    """
    Measure the real performance of the complete pipeline
    on the current PC.
    """

    print("\nCalibrating full processing pipeline...")

    sample_image_path = Path(sample_image_path)

    preprocess_times = []
    inference_times = []
    postprocess_times = []
    save_times = []

    for _ in range(runs):

        # -------------------------
        # PREPROCESS
        # -------------------------

        start = time.perf_counter()

        original_image, original_size, input_data = (
            remover.preprocess(sample_image_path)
        )

        preprocess_times.append(
            time.perf_counter() - start
        )

        # -------------------------
        # INFERENCE
        # -------------------------

        start = time.perf_counter()

        result = remover.infer_request.infer(
            {
                remover.input_layer: input_data
            }
        )

        inference_times.append(
            time.perf_counter() - start
        )

        # -------------------------
        # POSTPROCESS
        # -------------------------

        start = time.perf_counter()

        mask = result[remover.output_layer]

        import numpy as np

        mask = np.squeeze(mask)

        if remover.model_type == "birefnet":
            mask = 1 / (
                1 + np.exp(-mask)
            )

        mask = np.clip(mask, 0, 1)

        mask = (
            mask * 255
        ).astype(np.uint8)

        mask_image = Image.fromarray(mask)

        mask_image = mask_image.resize(
            original_size,
            Image.Resampling.LANCZOS
        )

        output_image = original_image.copy()
        output_image.putalpha(mask_image)

        postprocess_times.append(
            time.perf_counter() - start
        )

        # -------------------------
        # PNG SAVING
        # -------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".png",
            delete=False
        ) as temp_file:

            temp_path = temp_file.name

        start = time.perf_counter()

        output_image.save(
            temp_path,
            "PNG"
        )

        save_times.append(
            time.perf_counter() - start
        )

        Path(temp_path).unlink(
            missing_ok=True
        )

    return {
        "preprocess": (
            sum(preprocess_times)
            / len(preprocess_times)
        ),

        "inference": (
            sum(inference_times)
            / len(inference_times)
        ),

        "postprocess": (
            sum(postprocess_times)
            / len(postprocess_times)
        ),

        "save": (
            sum(save_times)
            / len(save_times)
        ),
    }


def estimate_total_time(
    calibration,
    image_count
):
    """
    Estimate total processing time using
    real measurements from the current PC.
    """

    estimated_per_image = (
        calibration["preprocess"]
        + calibration["inference"]
        + calibration["postprocess"]
        + calibration["save"]
    )

    estimated_total = (
        estimated_per_image
        * image_count
    )

    return {
        "estimated_per_image": estimated_per_image,
        "estimated_total": estimated_total,
    }


def format_time(seconds):

    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"

    if seconds < 60:
        return f"{seconds:.2f} seconds"

    minutes = int(seconds // 60)

    remaining_seconds = seconds % 60

    return (
        f"{minutes} min "
        f"{remaining_seconds:.1f} sec"
    )