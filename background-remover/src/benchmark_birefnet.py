import time
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import openvino as ov


MODEL_PATH = "models/birefnet_lite/onnx/model_fp16.onnx"

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

MODEL_WIDTH = 1024
MODEL_HEIGHT = 1024

MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def get_input_image():
    supported = {".jpg", ".jpeg", ".png", ".webp"}

    images = [
        file for file in INPUT_DIR.iterdir()
        if file.suffix.lower() in supported
    ]

    if not images:
        print("ERROR: No image found in input folder.")
        sys.exit(1)

    return images[0]


def preprocess(image_path):
    start = time.perf_counter()

    image = Image.open(image_path).convert("RGB")

    original_size = image.size

    resized = image.resize(
        (MODEL_WIDTH, MODEL_HEIGHT),
        Image.Resampling.LANCZOS
    )

    image_array = np.array(resized).astype(np.float32)

    image_array = image_array / 255.0

    image_array = (
        image_array - MEAN
    ) / STD

    image_array = np.transpose(
        image_array,
        (2, 0, 1)
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    elapsed = time.perf_counter() - start

    return (
        image,
        original_size,
        image_array,
        elapsed
    )


def run_benchmark(device, input_data):
    print(f"\nTesting {device}...")

    core = ov.Core()

    model = core.read_model(MODEL_PATH)

    compile_start = time.perf_counter()

    compiled_model = core.compile_model(
        model,
        device
    )

    compile_time = time.perf_counter() - compile_start

    infer_request = compiled_model.create_infer_request()

    input_layer = compiled_model.input(0)
    output_layer = compiled_model.output(0)

    print("Warming up...")

    infer_request.infer({
        input_layer: input_data
    })

    start = time.perf_counter()

    result = infer_request.infer({
        input_layer: input_data
    })

    inference_time = time.perf_counter() - start

    output = result[output_layer]

    return (
        output,
        inference_time,
        compile_time
    )


def sigmoid(x):
    return 1 / (
        1 + np.exp(-x)
    )


def postprocess(
    prediction,
    original_image,
    original_size
):
    start = time.perf_counter()

    mask = np.squeeze(prediction)

    mask = sigmoid(mask)

    mask = np.clip(mask, 0, 1)

    mask = (
        mask * 255
    ).astype(np.uint8)

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

    OUTPUT_DIR.mkdir(
        exist_ok=True
    )

    image_path = get_input_image()

    print("=" * 50)
    print("BIREFNET LITE BENCHMARK")
    print("=" * 50)

    print(f"Input image: {image_path}")

    original_image, original_size, input_data, preprocessing_time = (
        preprocess(image_path)
    )

    print(f"Original size: {original_size}")

    print(
        f"Model size: "
        f"{MODEL_WIDTH}x{MODEL_HEIGHT}"
    )

    results = {}

    for device in ["CPU", "GPU"]:

        try:

            (
                prediction,
                inference_time,
                compile_time
            ) = run_benchmark(
                device,
                input_data
            )

            output_image, postprocessing_time = (
                postprocess(
                    prediction,
                    original_image,
                    original_size
                )
            )

            output_path = (
                OUTPUT_DIR
                / f"birefnet_removed_{device.lower()}.png"
            )

            save_start = time.perf_counter()

            output_image.save(
                output_path,
                "PNG"
            )

            save_time = (
                time.perf_counter()
                - save_start
            )

            total_time = (
                preprocessing_time
                + inference_time
                + postprocessing_time
                + save_time
            )

            results[device] = total_time

            print("\n" + "=" * 40)
            print(f"{device} RESULTS")
            print("=" * 40)

            print(
                f"Model compile:  "
                f"{compile_time * 1000:.2f} ms"
            )

            print(
                f"Preprocessing:  "
                f"{preprocessing_time * 1000:.2f} ms"
            )

            print(
                f"Inference:      "
                f"{inference_time * 1000:.2f} ms"
            )

            print(
                f"Postprocessing: "
                f"{postprocessing_time * 1000:.2f} ms"
            )

            print(
                f"PNG saving:     "
                f"{save_time * 1000:.2f} ms"
            )

            print("-" * 40)

            print(
                f"TOTAL:          "
                f"{total_time * 1000:.2f} ms"
            )

        except Exception as error:

            print(
                f"\n{device} FAILED:"
            )

            print(error)

    if len(results) == 2:

        fastest = min(
            results,
            key=results.get
        )

        print("\n" + "=" * 50)

        print(
            f"FASTEST DEVICE: "
            f"{fastest}"
        )

        print("=" * 50)


if __name__ == "__main__":
    main()