import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"


def load_local_env() -> dict[str, str]:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return {}

    values = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    for filename in ("index.html", "styles.css"):
        shutil.copy2(ROOT / filename, DIST / filename)

    local_env = load_local_env()
    backend_url = os.getenv("VITE_API_URL", local_env.get("VITE_API_URL", ""))
    backend_url = backend_url.strip().rstrip("/")
    config = (
        "// Generated during the Vercel build.\n"
        f"window.BACKEND_URL = {backend_url!r};\n"
    )
    (DIST / "config.js").write_text(config, encoding="utf-8")


if __name__ == "__main__":
    main()