"""Staging batch 2: kumpulkan tambahan dari 3 dataset Kaggle + crop Roboflow.

Sumber:
1. owenlie/empon-dataset (CC BY-NC-SA 4.0)  - foto rimpang studio, 9 kelas
2. mohammadyusufibrahim/rimpang             - 5 kelas x 100
3. albertnathaniel12/indonesian-spices (ODbL) - ambil 4 kelas rimpang
4. staging_batch2/kunyit putih (crop Roboflow industri/empon v1)

Kebijakan:
- Kelas lemah (jahe merah, kunyit putih, temu hitam): ambil semua.
- Kelas kuat (sudah 540): maksimal MAX_STRONG per kelas agar seimbang.
- Dedup dhash terhadap dataset/ dan antar kandidat.
"""

from pathlib import Path

from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_DIR / "dataset"
STAGING_DIR = PROJECT_DIR / "staging_batch2" / "final"

CACHE = Path.home() / ".cache/kagglehub/datasets"
EMPON = CACHE / "owenlie/empon-dataset/versions/3/original/original"
RIMPANG = CACHE / "mohammadyusufibrahim/rimpang/versions/1/DATA 2"
SPICES = (
    CACHE
    / "albertnathaniel12/indonesian-spices-dataset/versions/11"
    / "Indonesian Spices Dataset"
)
ROBOFLOW_KP = PROJECT_DIR / "staging_batch2" / "kunyit putih"

# (folder sumber, kelas tujuan, prefix file)
SOURCES = [
    (EMPON / "jahe_merah", "jahe merah", "empon"),
    (EMPON / "kunyit_hitam", "temu hitam", "empon"),
    (EMPON / "kunyit_putih", "kunyit putih", "empon"),
    (ROBOFLOW_KP, "kunyit putih", "rfempon"),
    (EMPON / "jahe_putih", "jahe", "empon"),
    (EMPON / "jahe_emprit", "jahe", "empon"),
    (EMPON / "kunyit_kuning", "kunyit", "empon"),
    (EMPON / "kencur", "kencur", "empon"),
    (EMPON / "lengkuas", "lengkuas", "empon"),
    (EMPON / "temulawak", "temulawak", "empon"),
    (RIMPANG / "Jahe", "jahe", "yusuf"),
    (RIMPANG / "Kencur", "kencur", "yusuf"),
    (RIMPANG / "Kunyit", "kunyit", "yusuf"),
    (RIMPANG / "Lengkuas", "lengkuas", "yusuf"),
    (RIMPANG / "Temulawak", "temulawak", "yusuf"),
    (SPICES / "jahe", "jahe", "spices"),
    (SPICES / "kencur", "kencur", "spices"),
    (SPICES / "kunyit", "kunyit", "spices"),
    (SPICES / "lengkuas", "lengkuas", "spices"),
]

WEAK_CLASSES = {"jahe merah", "kunyit putih", "temu hitam"}
MAX_STRONG = 200
MIN_SIDE = 100
HASH_DISTANCE = 6
VALID_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


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


def load_existing_hashes(class_name):
    hashes = []
    class_dir = DATASET_DIR / class_name
    if not class_dir.is_dir():
        return hashes
    for path in sorted(class_dir.iterdir()):
        if path.suffix.lower() not in VALID_EXT:
            continue
        try:
            with Image.open(path) as img:
                hashes.append(dhash(img))
        except Exception:
            continue
    return hashes


def main():
    per_class_hashes = {}
    per_class_added = {}

    for source_dir, target_class, prefix in SOURCES:
        if not source_dir.is_dir():
            print("LEWATI (tidak ada):", source_dir)
            continue

        if target_class not in per_class_hashes:
            per_class_hashes[target_class] = load_existing_hashes(
                target_class
            )
            per_class_added[target_class] = 0

        limit = (
            None
            if target_class in WEAK_CLASSES
            else MAX_STRONG
        )

        out_dir = STAGING_DIR / target_class
        out_dir.mkdir(parents=True, exist_ok=True)

        taken = 0
        skipped = 0

        for path in sorted(source_dir.iterdir()):
            if path.suffix.lower() not in VALID_EXT:
                continue
            if limit is not None and per_class_added[target_class] >= limit:
                break

            try:
                with Image.open(path) as img:
                    img = img.convert("RGB")
                    if min(img.size) < MIN_SIDE:
                        skipped += 1
                        continue

                    image_hash = dhash(img)
                    if any(
                        hamming(image_hash, existing) <= HASH_DISTANCE
                        for existing in per_class_hashes[target_class]
                    ):
                        skipped += 1
                        continue

                    per_class_hashes[target_class].append(image_hash)
                    per_class_added[target_class] += 1
                    taken += 1

                    index = per_class_added[target_class]
                    output = out_dir / f"{prefix}_{index:04d}.jpg"

                    # Foto besar dikecilkan agar hemat ruang.
                    if max(img.size) > 1600:
                        img.thumbnail(
                            (1600, 1600),
                            Image.Resampling.LANCZOS,
                        )

                    img.save(output, "JPEG", quality=92)

            except Exception as error:
                print("Gagal:", path.name, error)

        print(
            f"{source_dir.parent.name}/{source_dir.name} -> "
            f"{target_class}: +{taken} (lewati {skipped})"
        )

    print()
    print("========== TOTAL TAMBAHAN ==========")
    for class_name in sorted(per_class_added):
        print(f"{class_name}: +{per_class_added[class_name]}")


if __name__ == "__main__":
    main()
