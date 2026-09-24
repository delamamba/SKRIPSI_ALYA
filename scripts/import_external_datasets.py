"""Impor dataset rimpang publik (Roboflow) ke dataset_external/.

Alur:
1. Unduh dataset YOLOv8 berlisensi jelas dan tanpa augmentasi.
2. Crop setiap bounding box menjadi gambar klasifikasi.
3. Buang kelas yang tidak dipakai proyek.
4. Deduplikasi perceptual (antar crop dan terhadap dataset internal).
5. Split train/valid/test berdasarkan gambar sumber (anti-leakage).

API key TIDAK ditulis di file ini. Simpan lewat terminal:
  read -s -p "Roboflow API key: " k && printf '%s' "$k" > ~/.roboflow_key \
    && chmod 600 ~/.roboflow_key && unset k && echo " tersimpan"
"""

from __future__ import annotations

import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml
from PIL import Image, ImageOps

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = PROJECT_DIR / "downloads_external"
EXTERNAL_DIR = PROJECT_DIR / "dataset_external"
INTERNAL_DIR = PROJECT_DIR / "dataset"

# Sumber terpilih: tanpa augmentasi, lisensi jelas, kelas relevan.
SOURCES = [
    {
        "name": "dimas_v4",
        "workspace": "skripsi-dimas",
        "project": "dataset-rimpang-0nrci",
        "version": 4,
        "license": "CC BY 4.0",
        "url": "https://universe.roboflow.com/skripsi-dimas/dataset-rimpang-0nrci",
    },
    {
        "name": "upn_v2",
        "workspace": "upn-veteran-yogyakarta",
        "project": "skripsi-rimpang",
        "version": 2,
        "license": "CC BY 4.0",
        "url": "https://universe.roboflow.com/upn-veteran-yogyakarta/skripsi-rimpang",
    },
    {
        "name": "taufiq_v8",
        "workspace": "ramadhantaufiq-9vaqr",
        "project": "pendeteksi-rimpang",
        "version": 8,
        "license": "Public Domain (CC0)",
        "url": "https://universe.roboflow.com/ramadhantaufiq-9vaqr/pendeteksi-rimpang",
    },
]

# Nama kelas sumber (lowercase) -> folder kelas proyek.
CLASS_MAP = {
    "jahe": "jahe",
    "kencur": "kencur",
    "kunyit": "kunyit",
    "lempuyang": "lempuyang",
    "lengkuas": "lengkuas",
    "temu kunci": "temu kunci",
    "temulawak": "temulawak",
}

SPLIT_BOUNDS = (70, 85)  # <70 train, <85 valid, sisanya test.
CAPS = {"train": 300, "valid": 60, "test": 60}
MIN_CROP_SIDE = 60
PAD_RATIO = 0.12
HASH_DISTANCE = 6


def read_api_key() -> str | None:
    key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if key:
        return key
    key_file = Path.home() / ".roboflow_key"
    if key_file.is_file():
        content = key_file.read_text(encoding="utf-8").strip()
        if content:
            return content
    return None


def dhash(image: Image.Image) -> int:
    gray = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
    pixels = list(gray.getdata())
    value = 0
    for row in range(8):
        for col in range(8):
            left = pixels[row * 9 + col]
            right = pixels[row * 9 + col + 1]
            value = (value << 1) | (1 if left > right else 0)
    return value


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def internal_hashes() -> list[int]:
    hashes = []
    for path in sorted(INTERNAL_DIR.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        try:
            with Image.open(path) as image:
                hashes.append(dhash(image))
        except OSError:
            continue
    return hashes


def split_for(stem: str) -> str:
    bucket = int(hashlib.md5(stem.encode("utf-8")).hexdigest(), 16) % 100
    if bucket < SPLIT_BOUNDS[0]:
        return "train"
    if bucket < SPLIT_BOUNDS[1]:
        return "valid"
    return "test"


def download_all(api_key: str) -> list[tuple[dict, Path]]:
    from roboflow import Roboflow

    client = Roboflow(api_key=api_key)
    results = []
    for source in SOURCES:
        target = DOWNLOAD_DIR / source["name"]
        marker = target / "data.yaml"
        if marker.is_file():
            print(f"[skip-unduh] {source['name']} sudah ada: {target}")
            results.append((source, target))
            continue
        print(f"[unduh] {source['workspace']}/{source['project']} v{source['version']} ...")
        project = client.workspace(source["workspace"]).project(source["project"])
        dataset = project.version(source["version"]).download(
            "yolov8", location=str(target), overwrite=True
        )
        results.append((source, Path(dataset.location)))
    return results


def iter_labels(dataset_dir: Path):
    names_file = dataset_dir / "data.yaml"
    names = yaml.safe_load(names_file.read_text(encoding="utf-8"))["names"]
    if isinstance(names, dict):
        names = [names[key] for key in sorted(names)]
    for split_dir in ("train", "valid", "test"):
        labels_dir = dataset_dir / split_dir / "labels"
        images_dir = dataset_dir / split_dir / "images"
        if not labels_dir.is_dir():
            continue
        for label_path in sorted(labels_dir.glob("*.txt")):
            image_path = None
            for extension in (".jpg", ".jpeg", ".png", ".webp"):
                candidate = images_dir / (label_path.stem + extension)
                if candidate.is_file():
                    image_path = candidate
                    break
            if image_path is None:
                continue
            yield names, label_path, image_path


def crop_boxes(source_name: str, dataset_dir: Path, seen: list[int], counters: dict) -> None:
    produced = 0
    dropped_class = 0
    dropped_small = 0
    dropped_dupe = 0
    dropped_cap = 0
    for names, label_path, image_path in iter_labels(dataset_dir):
        rows = [line.split() for line in label_path.read_text().splitlines() if line.strip()]
        if not rows:
            continue
        try:
            with Image.open(image_path) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                width, height = image.size
                for index, row in enumerate(rows):
                    class_name = names[int(row[0])].strip().lower()
                    target_class = CLASS_MAP.get(class_name)
                    if target_class is None:
                        dropped_class += 1
                        continue
                    cx, cy, bw, bh = (float(v) for v in row[1:5])
                    pad_w = bw * PAD_RATIO
                    pad_h = bh * PAD_RATIO
                    x1 = max(0, int((cx - bw / 2 - pad_w) * width))
                    y1 = max(0, int((cy - bh / 2 - pad_h) * height))
                    x2 = min(width, int((cx + bw / 2 + pad_w) * width))
                    y2 = min(height, int((cy + bh / 2 + pad_h) * height))
                    if x2 - x1 < MIN_CROP_SIDE or y2 - y1 < MIN_CROP_SIDE:
                        dropped_small += 1
                        continue
                    crop = image.crop((x1, y1, x2, y2))
                    signature = dhash(crop)
                    if any(hamming(signature, known) <= HASH_DISTANCE for known in seen):
                        dropped_dupe += 1
                        continue
                    split = split_for(f"{source_name}:{label_path.stem}")
                    if counters[(split, target_class)] >= CAPS[split]:
                        dropped_cap += 1
                        continue
                    seen.append(signature)
                    counters[(split, target_class)] += 1
                    out_dir = EXTERNAL_DIR / split / target_class
                    out_dir.mkdir(parents=True, exist_ok=True)
                    out_name = f"{source_name}_{label_path.stem}_{index}.jpg"
                    crop.save(out_dir / out_name, "JPEG", quality=92)
                    produced += 1
        except OSError as error:
            print(f"[lewati] {image_path.name}: {error}")
    print(
        f"[{source_name}] crop tersimpan={produced} | "
        f"kelas dibuang={dropped_class} kecil={dropped_small} "
        f"duplikat={dropped_dupe} cap={dropped_cap}"
    )


def main() -> int:
    api_key = read_api_key()
    if not api_key:
        print("API key Roboflow belum tersedia.")
        print("Jalankan perintah ini SENDIRI di terminal (key tidak lewat chat):")
        print(
            '  read -s -p "Roboflow API key: " k && printf \'%s\' "$k" > ~/.roboflow_key '
            "&& chmod 600 ~/.roboflow_key && unset k && echo \" tersimpan\""
        )
        print("Key gratis: https://app.roboflow.com/settings/api")
        return 2

    DOWNLOAD_DIR.mkdir(exist_ok=True)
    print("Menghitung hash dataset internal untuk deduplikasi ...")
    seen = internal_hashes()
    print(f"Hash internal: {len(seen)} gambar")

    counters: dict = defaultdict(int)
    for split_dir in ("train", "valid", "test"):
        for class_dir in (EXTERNAL_DIR / split_dir).glob("*"):
            if class_dir.is_dir():
                counters[(split_dir, class_dir.name)] = sum(
                    1 for item in class_dir.iterdir() if item.is_file()
                )

    for source, dataset_dir in download_all(api_key):
        print(f"\n== {source['name']} ({source['license']}) ==")
        crop_boxes(source["name"], dataset_dir, seen, counters)

    print("\n================ RINGKASAN dataset_external ================")
    for split_dir in ("train", "valid", "test"):
        print(split_dir.upper())
        for class_dir in sorted((EXTERNAL_DIR / split_dir).glob("*")):
            if class_dir.is_dir():
                total = sum(1 for item in class_dir.iterdir() if item.is_file())
                print(f"  {class_dir.name:14}: {total}")
    print("=============================================================")
    print("Atribusi lisensi (wajib dicantumkan di skripsi):")
    for source in SOURCES:
        print(f"  - {source['url']} ({source['license']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
