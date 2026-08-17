from pathlib import Path

from huggingface_hub import hf_hub_download


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "onnx" / "model_fp16.onnx"


def main() -> None:
    if MODEL_PATH.exists():
        print(f"MODNet model already exists at {MODEL_PATH}")
        return

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    downloaded_path = hf_hub_download(
        repo_id="onnx-community/modnet-webnn",
        filename="onnx/model_fp16.onnx",
        local_dir=PROJECT_ROOT / "models",
    )
    print(f"Downloaded MODNet model to {downloaded_path}")


if __name__ == "__main__":
    main()