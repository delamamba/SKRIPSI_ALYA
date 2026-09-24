"""Impor crop kunyit_putih dari Roboflow industri/empon v1.

Versi 1 adalah versi augmented, sehingga satu gambar sumber bisa muncul
beberapa kali. Untuk menghindari duplikasi/leakage, hanya SATU crop per
gambar sumber yang diambil (box kunyit_putih terbesar), lalu di-dedup
dengan dhash terhadap foto kunyit putih yang sudah ada.
"""

import os
import sys
from pathlib import Path

import yaml
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = PROJECT_DIR / "downloads_batch2" / "empon_v1"
STAGING_DIR = PROJECT_DIR / "staging_batch2" / "kunyit putih"
EXISTING_DIR = PROJECT_DIR / "dataset" / "kunyit putih"

TARGET_CLASS = "kunyit_putih"
PAD_RATIO = 0.12
MIN_SIDE = 60
HASH_DISTANCE = 6


def read_api_key():
    env_key = os.environ.get("ROBOFLOW_API_KEY", "").strip()
    if env_key:
        return env_key
    key_file = Path.home() / ".roboflow_key"
    if key_file.exists():
        return key_file.read_text().strip()
    raise SystemExit("API key Roboflow tidak ditemukan.")


def download():
    if DOWNLOAD_DIR.exists() and any(DOWNLOAD_DIR.rglob("*.jpg")):
        print("Unduhan sudah ada, lewati:", DOWNLOAD_DIR)
        return
    from roboflow import Roboflow

    rf = Roboflow(api_key=read_api_key())
    project = rf.workspace("industri").project("empon")
    version = project.version(1)
    version.download(
        "yolov8",
        location=str(DOWNLOAD_DIR),
        overwrite=True,
    )
    print("Unduhan selesai:", DOWNLOAD_DIR)


def dhash(image, size=8):
    gray = image.convert("L").resize(
        (size + 1, size),
        Image.Resampling.LANCZOS,
    )
    pixels = list(gray.getdata())
    bits = 0
    for row in range(size):
        for col in range(size):
            left = pixels[row * (size + 1) + col]
            right = pixels[row * (size + 1) + col + 1]
            bits = (bits << 1) | (1 if left > right else 0)
    return bits


def hamming(a, b):
    return bin(a ^ b).count("1")


def source_stem(filename):
    stem = Path(filename).stem
    marker = "_jpg.rf."
    if marker in stem:
        return stem.split(marker)[0]
    return stem


def collect_boxes():
    data_yaml = DOWNLOAD_DIR / "data.yaml"
    names = yaml.safe_load(data_yaml.read_text())["names"]
    if isinstance(names, dict):
        names = [names[key] for key in sorted(names)]

    if TARGET_CLASS not in names:
        raise SystemExit(f"Kelas {TARGET_CLASS} tidak ada di {names}")

    target_id = names.index(TARGET_CLASS)
    best_per_source = {}

    for split in ("train", "valid", "test"):
        image_dir = DOWNLOAD_DIR / split / "images"
        label_dir = DOWNLOAD_DIR / split / "labels"
        if not image_dir.is_dir():
            continue

        for image_path in sorted(image_dir.iterdir()):
            if image_path.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            label_path = label_dir / (image_path.stem + ".txt")
            if not label_path.exists():
                continue

            boxes = []
            for line in label_path.read_text().splitlines():
                parts = line.split()
                if len(parts) < 5:
                    continue
                class_id = int(float(parts[0]))
                if class_id != target_id:
                    continue
                cx, cy, w, h = map(float, parts[1:5])
                boxes.append((w * h, cx, cy, w, h))

            if not boxes:
                continue

            boxes.sort(reverse=True)
            area, cx, cy, w, h = boxes[0]
            key = source_stem(image_path.name)
            current = best_per_source.get(key)
            if current is None or area > current[0]:
                best_per_source[key] = (
                    area,
                    image_path,
                    (cx, cy, w, h),
                )

    print("Gambar sumber unik dengan kunyit_putih:", len(best_per_source))
    return best_per_source


def crop_and_save(best_per_source):
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    existing_hashes = []
    for path in sorted(EXISTING_DIR.iterdir()):
        try:
            with Image.open(path) as img:
                existing_hashes.append(dhash(img))
        except Exception:
            continue

    saved = 0
    skipped_small = 0
    skipped_dup = 0
    new_hashes = []

    for index, key in enumerate(sorted(best_per_source), start=1):
        _, image_path, (cx, cy, w, h) = best_per_source[key]

        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                width, height = img.size

                box_w = w * width
                box_h = h * height
                pad_x = box_w * PAD_RATIO
                pad_y = box_h * PAD_RATIO

                left = max(0, cx * width - box_w / 2 - pad_x)
                top = max(0, cy * height - box_h / 2 - pad_y)
                right = min(width, cx * width + box_w / 2 + pad_x)
                bottom = min(height, cy * height + box_h / 2 + pad_y)

                if (right - left) < MIN_SIDE or (bottom - top) < MIN_SIDE:
                    skipped_small += 1
                    continue

                crop = img.crop(
                    (int(left), int(top), int(right), int(bottom))
                )

                crop_hash = dhash(crop)
                duplicate = any(
                    hamming(crop_hash, other) <= HASH_DISTANCE
                    for other in existing_hashes + new_hashes
                )
                if duplicate:
                    skipped_dup += 1
                    continue

                new_hashes.append(crop_hash)
                output = STAGING_DIR / f"empon_kunyit_putih_{index:03d}.jpg"
                crop.save(output, "JPEG", quality=95)
                saved += 1

        except Exception as error:
            print("Gagal:", image_path.name, error)

    print("Crop tersimpan :", saved)
    print("Terlalu kecil  :", skipped_small)
    print("Duplikat       :", skipped_dup)
    print("Lokasi         :", STAGING_DIR)


def main():
    download()
    best = collect_boxes()
    crop_and_save(best)


if __name__ == "__main__":
    sys.exit(main())
