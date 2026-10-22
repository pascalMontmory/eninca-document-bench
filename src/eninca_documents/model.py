"""Explicit pinned model download. No document content is sent to a service."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import urllib.request


def model_lock():
    return json.loads(Path(__file__).with_name("model.lock.json").read_text())


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_model(directory):
    lock = model_lock()
    for name, record in lock["files"].items():
        path = Path(directory) / name
        if not path.is_file() or path.stat().st_size != record["size"] or file_sha256(path) != record["sha256"]:
            raise ValueError(f"Missing or changed model file: {name}; run fetch-model in a new directory")
    return lock


def fetch_model(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    lock = model_lock()
    needed = sum(r["size"] for name, r in lock["files"].items() if not (directory / name).exists())
    if shutil.disk_usage(directory).free < needed + 100_000_000:
        raise OSError("Insufficient free space for model and 100 MB working margin")
    for name, record in lock["files"].items():
        destination = directory / name
        if destination.exists():
            if destination.stat().st_size != record["size"] or file_sha256(destination) != record["sha256"]:
                raise ValueError(f"Refusing to replace changed file: {destination}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        url = f'https://huggingface.co/{lock["model_id"]}/resolve/{lock["revision"]}/{name}'
        print(f"Downloading {name} ({record['size']} bytes)", flush=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as out:
                temporary = Path(out.name)
                with urllib.request.urlopen(url, timeout=90) as response:
                    shutil.copyfileobj(response, out, length=1024 * 1024)
            if temporary.stat().st_size != record["size"] or file_sha256(temporary) != record["sha256"]:
                raise ValueError(f"Downloaded file hash mismatch: {name}")
            temporary.replace(destination)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    verify_model(directory)
