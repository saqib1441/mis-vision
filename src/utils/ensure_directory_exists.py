from pathlib import Path


def ensure_directory_exists():
    root = Path(__file__).resolve().parents[2]

    folders = [root / "voices", root / "cloned_voices", root / "outputs"]

    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
