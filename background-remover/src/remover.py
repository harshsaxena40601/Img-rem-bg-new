from pathlib import Path
import time

import numpy as np
from PIL import Image
import openvino as ov


class BackgroundRemover:
    def __init__(
        self,
        model_path,
        device="CPU",
        model_type="modnet"
    ):
        self.model_path = model_path
        self.device = device
        self.model_type = model_type

        self.core = ov.Core()

        print(f"Loading {model_type} model on {device}...")

        model = self.core.read_model(model_path)

        self.compiled_model = self.core.compile_model(
            model,
            device
        )

        self.input_layer = self.compiled_model.input(0)
        self.output_layer = self.compiled_model.output(0)

        self.infer_request = (
            self.compiled_model.create_infer_request()
        )

        print("Model loaded successfully.")

    def preprocess(self, image_path):
        image = Image.open(image_path).convert("RGB")

        original_size = image.size

        if self.model_type == "modnet":
            size = (512, 512)

            image_array = np.array(
                image.resize(
                    size,
                    Image.Resampling.LANCZOS
                )
            ).astype(np.float32)

            image_array = image_array / 255.0

        elif self.model_type == "birefnet":
            size = (1024, 1024)

            image_array = np.array(
                image.resize(
                    size,
                    Image.Resampling.LANCZOS
                )
            ).astype(np.float32)

            image_array = image_array / 255.0

            mean = np.array(
                [0.485, 0.456, 0.406],
                dtype=np.float32
            )

            std = np.array(
                [0.229, 0.224, 0.225],
                dtype=np.float32
            )

            image_array = (
                image_array - mean
            ) / std

        else:
            raise ValueError(
                f"Unsupported model type: {self.model_type}"
            )

        image_array = np.transpose(
            image_array,
            (2, 0, 1)
        )

        image_array = np.expand_dims(
            image_array,
            axis=0
        )

        return (
            image,
            original_size,
            image_array
        )

    def remove(self, image_path):
        total_start = time.perf_counter()

        preprocess_start = time.perf_counter()

        original_image, original_size, input_data = (
            self.preprocess(image_path)
        )

        preprocess_time = (
            time.perf_counter()
            - preprocess_start
        )

        inference_start = time.perf_counter()

        result = self.infer_request.infer(
            {
                self.input_layer: input_data
            }
        )

        inference_time = (
            time.perf_counter()
            - inference_start
        )

        postprocess_start = time.perf_counter()

        mask = result[self.output_layer]

        mask = np.squeeze(mask)

        if self.model_type == "birefnet":
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

        postprocess_time = (
            time.perf_counter()
            - postprocess_start
        )

        total_time = (
            time.perf_counter()
            - total_start
        )

        return {
            "image": output_image,
            "preprocess_time": preprocess_time,
            "inference_time": inference_time,
            "postprocess_time": postprocess_time,
            "total_time": total_time
        }

    def save(self, result, output_path):
        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        save_start = time.perf_counter()

        result["image"].save(
            output_path,
            "PNG"
        )

        save_time = (
            time.perf_counter()
            - save_start
        )

        return save_time