import time
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import openvino as ov


MODEL_PATH = "models/onnx/model_fp16.onnx"
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

TEST_SIZE = 512


def get_input_image():
    supported = {".jpg", ".jpeg", ".png", ".webp"}

    images = [
        file for file in INPUT_DIR.iterdir()
        if file.suffix.lower() in supported
    ]

    if not images:
        print("ERROR: No image found in the input folder.")
        print("Add a JPG, PNG, or WEBP image to the input folder.")
        sys.exit(1)

    return images[0]


def preprocess(image_path):
    start = time.perf_counter()

    image = Image.open(image_path).convert("RGB")

    original_size = image.size

    resized = image.resize(
        (TEST_SIZE, TEST_SIZE),
        Image.Resampling.LANCZOS
    )

    image_array = np.array(resized).astype(np.float32)

    image_array = image_array / 255.0

    image_array = np.transpose(
        image_array,
        (2, 0, 1)
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    elapsed = time.perf_counter() - start

    return image, original_size, image_array, elapsed


def run_benchmark(device, input_data):
    print(f"\nTesting {device}...")

    core = ov.Core()

    model = core.read_model(MODEL_PATH)

    compiled_model = core.compile_model(
        model,
        device
    )

    infer_request = compiled_model.create_infer_request()

    input_layer = compiled_model.input(0)
    output_layer = compiled_model.output(0)

    # Warm-up run
    infer_request.infer({
        input_layer: input_data
    })

    start = time.perf_counter()

    result = infer_request.infer({
        input_layer: input_data
    })

    inference_time = time.perf_counter() - start

    output = result[output_layer]

    return output, inference_time


def postprocess(mask, original_image, original_size):
    start = time.perf_counter()

    mask = np.squeeze(mask)

    mask = np.clip(mask, 0, 1)

    mask = (mask * 255).astype(np.uint8)

    mask_image = Image.fromarray(mask)

    mask_image = mask_image.resize(
        original_size,
        Image.Resampling.LANCZOS
    )

    result = original_image.copy()

    result.putalpha(mask_image)

    elapsed = time.perf_counter() - start

    return result, elapsed


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    image_path = get_input_image()

    print(f"Input image: {image_path}")

    print("\nPreprocessing...")

    original_image, original_size, input_data, preprocessing_time = preprocess(
        image_path
    )

    print(f"Original size: {original_size}")
    print(f"Model size: {TEST_SIZE}x{TEST_SIZE}")

    results = {}

    for device in ["CPU", "GPU"]:
        try:
            mask, inference_time = run_benchmark(
                device,
                input_data
            )

            output_image, postprocessing_time = postprocess(
                mask,
                original_image,
                original_size
            )

            total_time = (
                preprocessing_time
                + inference_time
                + postprocessing_time
            )

            output_path = OUTPUT_DIR / f"removed_{device.lower()}.png"

            save_start = time.perf_counter()

            output_image.save(
                output_path,
                "PNG"
            )

            save_time = time.perf_counter() - save_start

            total_time += save_time

            results[device] = total_time

            print(f"\n{device} RESULTS")
            print("-" * 30)
            print(f"Preprocessing:  {preprocessing_time * 1000:.2f} ms")
            print(f"Inference:      {inference_time * 1000:.2f} ms")
            print(f"Postprocessing: {postprocessing_time * 1000:.2f} ms")
            print(f"PNG saving:     {save_time * 1000:.2f} ms")
            print(f"TOTAL:          {total_time * 1000:.2f} ms")

        except Exception as error:
            print(f"\n{device} FAILED")
            print(error)

    if len(results) == 2:
        fastest = min(results, key=results.get)

        print("\n" + "=" * 40)
        print(f"FASTEST DEVICE: {fastest}")
        print("=" * 40)

        slower = max(results.values())
        faster = min(results.values())

        improvement = ((slower - faster) / slower) * 100

        print(f"Speed improvement: {improvement:.2f}%")


if __name__ == "__main__":
    main()