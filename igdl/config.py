import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".igdl"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def get_download_dir() -> Path | None:
    cfg = get_config()
    d = cfg.get("download_dir")
    return Path(d) if d else None


def set_download_dir(path: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    resolved.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = get_config()
    cfg["download_dir"] = str(resolved)
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)
    return resolved
