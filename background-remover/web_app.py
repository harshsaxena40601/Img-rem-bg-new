from __future__ import annotations

import io
import os
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

from device_info import get_device_info
from estimator import calibrate_pipeline, estimate_total_time, format_time
from main import DEVICE, MODEL_PATH, MODEL_TYPE
from remover import BackgroundRemover


PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_ROOT / "output"
ALLOWED_EXTENSIONS = {".avif", ".jpeg", ".jpg", ".png", ".webp"}
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
CORS(
    app,
    resources={r"/*": {"origins": [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "*").split(",")
        if origin.strip()
    ]}},
    expose_headers=[
        "X-Processing-Time-Ms",
        "X-Preprocess-Time-Ms",
        "X-Inference-Time-Ms",
        "X-Postprocess-Time-Ms",
        "X-Save-Time-Ms",
        "X-Total-Time-Ms",
        "X-Model",
    ],
)

_remover: BackgroundRemover | None = None
_remover_lock = threading.Lock()
_inference_lock = threading.Lock()
_runtime_lock = threading.Lock()
_runtime = {
    "initialized": False,
    "ready": False,
    "error": None,
    "device_info": None,
    "calibration": None,
    "estimate": None,
    "startup_time": None,
}


def get_remover() -> BackgroundRemover:
    global _remover

    if _remover is None:
        with _remover_lock:
            if _remover is None:
                if not MODEL_PATH.exists():
                    raise FileNotFoundError(
                        f"Model not found at {MODEL_PATH}. "
                        "Run the model download step from setup.txt."
                    )
                _remover = BackgroundRemover(
                    model_path=str(MODEL_PATH),
                    device=DEVICE,
                    model_type=MODEL_TYPE,
                )
    return _remover


def _format_measurements(measurements: dict[str, float]) -> dict[str, object]:
    return {
        key: {
            "seconds": round(value, 6),
            "milliseconds": round(value * 1000),
            "formatted": format_time(value),
        }
        for key, value in measurements.items()
    }


def initialize_runtime() -> None:
    """Load and warm the model before the first browser upload."""
    if _runtime["initialized"]:
        return

    with _runtime_lock:
        if _runtime["initialized"]:
            return

        started = time.perf_counter()
        try:
            _runtime["device_info"] = get_device_info()
            remover = get_remover()

            samples = sorted(
                path
                for path in (PROJECT_ROOT / "input").iterdir()
                if path.is_file() and is_supported(path.name)
            )
            if not samples:
                raise FileNotFoundError(
                    "No sample image is available for performance calibration."
                )

            # This measures the real machine and also warms the compiled model.
            calibration = calibrate_pipeline(
                remover,
                samples[0],
                runs=3,
            )
            estimate = estimate_total_time(calibration, 1)
            _runtime["calibration"] = _format_measurements(calibration)
            _runtime["estimate"] = {
                "estimated_per_image": _format_measurements(
                    {"time": estimate["estimated_per_image"]}
                )["time"],
                "estimated_total": _format_measurements(
                    {"time": estimate["estimated_total"]}
                )["time"],
            }
            _runtime["ready"] = True
            app.logger.info(
                "Runtime ready on %s; estimated per image: %s",
                DEVICE,
                format_time(estimate["estimated_per_image"]),
            )
        except Exception as error:
            _runtime["error"] = str(error)
            app.logger.exception("Runtime initialization failed")
        finally:
            _runtime["startup_time"] = round(
                time.perf_counter() - started,
                3,
            )
            _runtime["initialized"] = True


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    initialize_runtime()
    return jsonify(
        {
            "status": "ok" if _runtime["ready"] else "error",
            "ready": _runtime["ready"],
            "error": _runtime["error"],
            "model": MODEL_TYPE,
            "device": DEVICE,
            "model_exists": MODEL_PATH.exists(),
            "device_info": _runtime["device_info"],
            "calibration": _runtime["calibration"],
            "estimate": _runtime["estimate"],
            "startup_seconds": _runtime["startup_time"],
        }
    )


@app.post("/process")
def process_image():
    initialize_runtime()
    if not _runtime["ready"]:
        return jsonify(
            {"error": _runtime["error"] or "Runtime is not ready yet."}
        ), 503

    upload = request.files.get("image")

    if upload is None or not upload.filename:
        return jsonify({"error": "Choose an image before processing."}), 400

    filename = secure_filename(upload.filename)
    if not is_supported(filename):
        return jsonify(
            {
                "error": "Unsupported image type. Use JPG, PNG, WEBP, or AVIF."
            }
        ), 400

    input_path: Path | None = None
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        input_path = OUTPUT_DIR / f".upload-{uuid.uuid4().hex}{Path(filename).suffix}"
        upload.save(input_path)

        remover = get_remover()
        # The OpenVINO infer request is shared by the cached model instance.
        with _inference_lock:
            result = remover.remove(input_path)

        output_name = f"{Path(filename).stem}_removed.png"
        output_path = OUTPUT_DIR / f"web-{uuid.uuid4().hex}-{output_name}"
        save_time = remover.save(result, output_path)

        image_buffer = io.BytesIO()
        result["image"].save(image_buffer, format="PNG")
        image_buffer.seek(0)

        response = send_file(
            image_buffer,
            mimetype="image/png",
            as_attachment=False,
            download_name=output_name,
        )
        response.headers["X-Processing-Time-Ms"] = str(
            round(result["total_time"] * 1000)
        )
        response.headers["X-Preprocess-Time-Ms"] = str(
            round(result["preprocess_time"] * 1000)
        )
        response.headers["X-Inference-Time-Ms"] = str(
            round(result["inference_time"] * 1000)
        )
        response.headers["X-Postprocess-Time-Ms"] = str(
            round(result["postprocess_time"] * 1000)
        )
        response.headers["X-Save-Time-Ms"] = str(round(save_time * 1000))
        response.headers["X-Total-Time-Ms"] = str(
            round((result["total_time"] + save_time) * 1000)
        )
        response.headers["X-Model"] = MODEL_TYPE
        return response
    except Exception as error:
        app.logger.exception("Background removal failed")
        return jsonify({"error": str(error)}), 500
    finally:
        if input_path is not None:
            input_path.unlink(missing_ok=True)


@app.errorhandler(413)
def payload_too_large(_error):
    return jsonify({"error": "Image is too large. Maximum size is 20 MB."}), 413


if __name__ == "__main__":
    initialize_runtime()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )