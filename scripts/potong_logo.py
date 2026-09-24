"""Potong ikon dari logo lengkap + siapkan versi web (sekali pakai)."""
from PIL import Image, ImageDraw

SRC = r"C:\Users\Administrator\Downloads\logo.png"
OUT_ICON = r"d:\SKRIPSI_ALYA\static\plants\logo.png"
OUT_FULL = r"d:\SKRIPSI_ALYA\static\plants\logo_full.png"

img = Image.open(SRC)
print("Sumber:", img.size, img.mode)

rgba = img.convert("RGBA")
w, h = rgba.size
px = rgba.load()

# Mask non-putih (dan non-transparan)
def is_content(x, y):
    r, g, b, a = px[x, y]
    return a > 20 and not (r > 240 and g > 240 and b > 240)

# Jumlah piksel konten per kolom
col_counts = []
for x in range(w):
    c = 0
    for y in range(0, h, 2):  # sampling tiap 2 baris agar cepat
        if is_content(x, y):
            c += 1
    col_counts.append(c)

# Batas kiri konten
xs = [x for x, c in enumerate(col_counts) if c > 0]
left, right = xs[0], xs[-1]

# Cari celah putih pertama setelah ikon (>= 15 kolom kosong berturut-turut)
gap_start = None
run = 0
for x in range(left + int(0.15 * w), right):
    if col_counts[x] == 0:
        run += 1
        if run >= 15:
            gap_start = x - run + 1
            break
    else:
        run = 0

icon_right = gap_start if gap_start else left + int(0.4 * w)
print(f"Konten: x {left}..{right} | batas ikon: {icon_right}")

# BBox vertikal wilayah ikon
ys = []
for y in range(h):
    for x in range(left, icon_right, 2):
        if is_content(x, y):
            ys.append(y)
            break
top, bottom = ys[0], ys[-1]

# Crop ikon + padding 4%
pad = int(0.04 * max(icon_right - left, bottom - top))
box = (max(0, left - pad), max(0, top - pad),
       min(w, icon_right + pad), min(h, bottom + pad))
icon = rgba.crop(box)

# Kanvas persegi transparan
side = max(icon.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(icon, ((side - icon.size[0]) // 2, (side - icon.size[1]) // 2), icon)

# Background putih -> transparan (flood fill dari 4 sudut)
solid = canvas.copy()
for corner in [(0, 0), (side - 1, 0), (0, side - 1), (side - 1, side - 1)]:
    ImageDraw.floodfill(solid, corner, (0, 0, 0, 0), thresh=25)

solid.save(OUT_ICON)
print("Ikon:", solid.size, "->", OUT_ICON)

# Versi lengkap: trim seluruh konten + padding
ys_full = []
for y in range(h):
    for x in range(left, right, 3):
        if is_content(x, y):
            ys_full.append(y)
            break
ft, fb = ys_full[0], ys_full[-1]
padf = int(0.03 * (right - left))
full = rgba.crop((max(0, left - padf), max(0, ft - padf),
                  min(w, right + padf), min(h, fb + padf)))
for corner in [(0, 0), (full.size[0] - 1, 0), (0, full.size[1] - 1),
               (full.size[0] - 1, full.size[1] - 1)]:
    ImageDraw.floodfill(full, corner, (0, 0, 0, 0), thresh=25)
full.save(OUT_FULL)
print("Full:", full.size, "->", OUT_FULL)
