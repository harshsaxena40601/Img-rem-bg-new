# Background Remover

## Overview

This project removes image backgrounds with OpenVINO models and includes timing
estimation, image analysis, and a BiRefNet benchmark. A product-image-generator
prototype is also included under `background-remover/product-image-generator`.

## Running on Replit

The project uses Replit's managed Python 3.11 environment rather than the
Windows `.venv` activation command in the original `setup.txt`.

```bash
cd background-remover
PYTHONPATH=src python src/main.py
```

For the browser frontend, use:

```bash
cd background-remover
PYTHONPATH=src python web_app.py
```

Then open the Replit preview, upload an image, and click **Remove background**.
The frontend uses the same `MODEL_PATH`, `MODEL_TYPE`, `DEVICE`, and
`BackgroundRemover` implementation as the CLI in `src/main.py` and `src/remover.py`.

Input images belong in `background-remover/input/`. Generated transparent PNGs
are written to `background-remover/output/`.

The downloaded models are stored at:

- `background-remover/models/onnx/model_fp16.onnx` (MODNet)
- `background-remover/models/birefnet_lite/onnx/model_fp16.onnx` (BiRefNet Lite)

The Replit workflow runs the Flask frontend on port 5000. The original batch
CLI remains available as a separate manual command.

## Dependencies

Dependencies are declared in `pyproject.toml`. The project uses CPU OpenVINO
inference in this environment. The BiRefNet benchmark may report a GPU
OpenCL-load failure when no GPU/OpenCL runtime is available; its CPU benchmark
remains supported.

## Render and Vercel deployment

Deployment files are included for hosting the Flask API on Render and the
standalone frontend on Vercel. See `DEPLOYMENT.md` for the required build
commands and environment variables. Render downloads the ignored MODNet model
during its build; Vercel only serves the static files in `frontend/`. For local
frontend switching, change the single `VITE_API_URL` value in `frontend/.env`.
The Render Gunicorn command includes `PYTHONPATH=src` so the shared pipeline
modules load correctly in production.

## User preferences

- Keep the existing project structure and model choices.