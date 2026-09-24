from pathlib import Path
import math
import traceback

import torch
import torch.nn as nn
import torch.nn.functional as F

from PIL import Image, ImageOps

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

import torchvision.transforms as transforms

from torchvision.models import (
    resnet50,
    vit_b_16
)

from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge


# ============================================================
# RIMPANG AI
# WEB IDENTIFICATION
# HYBRID RESNET-50 + VIT-B/16
# ============================================================


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR / "hybrid_resnet_vit_best.pth"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# UPLOAD
# ============================================================

UPLOAD_FOLDER = BASE_DIR / "uploads"

UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = str(
    UPLOAD_FOLDER
)

app.config["MAX_CONTENT_LENGTH"] = (
    10 * 1024 * 1024
)


# ============================================================
# FORMAT GAMBAR
# ============================================================

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png",
    "webp"
}


# ============================================================
# 10 KELAS
# ============================================================

CLASS_NAMES = [

    "Jahe",
    "Jahe Merah",
    "Kencur",
    "Kunyit",
    "Kunyit Putih",
    "Lempuyang",
    "Lengkuas",
    "Temu Hitam",
    "Temu Kunci",
    "Temulawak"

]


NUM_CLASSES = len(
    CLASS_NAMES
)


# ============================================================
# INFORMASI TANAMAN
# ============================================================
#
# Catatan:
# Khasiat di sini ditulis sebagai PEMANFAATAN TRADISIONAL,
# bukan sebagai klaim bahwa tanaman menyembuhkan penyakit.
# Untuk skripsi, sumber ilmiah tetap dicantumkan pada
# bagian referensi penelitian.
# ============================================================

PLANT_INFO = {

    "Jahe Merah": {

        "scientific_name":
            "Zingiber officinale var. rubrum",

        "benefits": [

            "Mampu mengurangi peradangan pada sel saraf .",
            "Membantu menghambat pertumbuhan bakteri penyebab penyakit..",
            "Mengurangi penggumpalan trombosit secara alami.."

        ],
        "processing": [
    
        {
        "disease": "Keluhan Peredaran Darah Kurang Lancar",
        "recipe": "Cuci bersih 3 ruas jahe merah, memarkan, kemudian rebus bersama 400 ml air dan 2 lembar daun pandan selama 15 menit. Minuman diminum hangat satu kali sehari."
        },
        {
        "disease": "Tubuh Mudah Lelah Setelah Aktivitas Berat",
        "recipe": "Jahe merah diparut, dicampur sedikit madu dan air hangat, kemudian disaring sebelum diminum."
        },
        {
        "disease": "Nyeri Sendi Yang Cukup Berat",
        "recipe": "Iris tipis jahe merah, rebus bersama serai dan kayu manis hingga tersisa sekitar 250 ml air rebusan."
        }
        ]
    },

    "Jahe": {

        "scientific_name":
            "Zingiber officinale",

        "benefits": [

            "Dapat membantu mengurangi migren yang berlebihan.",
            "Membantu pada kesehatan reproduksi pria.",
            "Membantu pengaturan kadar glukosa serta membantu metabolisme karbohidrat."

        ],
        "processing": [
        {
        "disease": "Gangguan Pencernaan",
        "recipe": "Jahe diiris tipis, direbus bersama biji adas selama 10 menit, lalu diminum setelah makan."
        },
        {
        "disease": "Mual Saat Perjalanan atau Mabuk",
        "recipe": "Seduh irisan jahe segar dengan air panas selama 5–7 menit tanpa direbus agar aroma atsirinya tetap terjaga."
        },
        {
        "disease": "Batuk Berdahak Ringan",
        "recipe": "Jahe direbus bersama daun mint dan sedikit gula batu hingga air berubah kekuningan."
        }
        ]

    },

    "Kencur": {

        "scientific_name":
            "Kaempferia galanga",

        "benefits": [

            "Berpotensi sebagai antikanker.",
            "Membantu mengurangi pembengkakan akibat peradangan.",
            "membantu menghambat pertumbuhan bakteri penyebab jerawat."

        ],
        "processing": [
        {
        "disease": "Batuk Berdahak/Berlendir",
        "recipe": "Rimpang kencur diparut, diperas, kemudian dicampur madu sebelum diminum."
        },
        {
        "disease": "Pegal dan Nyeri Otot",
        "recipe": "Kencur ditumbuk bersama sedikit beras, kemudian dijadikan baluran pada bagian tubuh yang terasa pegal."
        },
        {
        "disease": "Nafsu Makan Menurun",
        "recipe": "Kencur direbus bersama daun pandan dan gula aren menjadi minuman tradisional."
        }
        ]

    },


    "Kunyit Putih": {

        "scientific_name":
            "Curcuma zedoaria",

        "benefits": [

            "Membantu melindungi sel hati dari kerusakan akibat radikal bebas.",
            "Mengurangi peradangan pada sistem saraf.",
            "Membantu memperlambat proses penuaan sel."

        ],
        "processing": [
        {
        "disease": "Perut Terasa Kembung",
        "recipe": "Kunyit putih dipotong kecil lalu direbus bersama daun salam selama 15 menit."
        },
        {
        "disease": "Keluhan Lambung Yang Akut",
        "recipe": "Air rebusan kunyit putih diminum hangat sebelum makan."
        },
        {
        "disease": "Pemanfaatan Herbal Setelah Melahirkan",
        "recipe": "Kunyit putih direbus bersama temu kunci dan daun sirih sebagai ramuan tradisional."
        }
        ]

    },


    "Kunyit": {

        "scientific_name":
            "Curcuma longa",

        "benefits": [

            "Berpotensi menurunkan risiko penyakit Alzheimer dan Parkinson.",
            "Menghambat pembentukan pembuluh darah baru pada jaringan tumor.",
            "Mendukung sistem imun karena sebagian besar imun berasal dari usus."

        ],
        "processing": [
        {
        "disease": "Nyeri Haid Yang Berlebihan",
        "recipe": "Kunyit diparut lalu direbus bersama asam jawa dan gula aren menjadi minuman kunyit asam."
        },
        {
        "disease": "Gangguan Pencernaan",
        "recipe": "Kunyit direbus bersama daun salam hingga tersisa satu gelas air."
        },
        {
        "disease": "Perawatan PadaKulit",
        "recipe": "Kunyit dihaluskan bersama madu dan dijadikan masker alami selama 15 menit."
        }
        ]

    },


    "Lempuyang": {

        "scientific_name":
            "Zingiber zerumbet",

        "benefits": [

            "menghambat proses inflamasi yang mendukung pertumbuhan tumor.",
            "Membantu menghambat pertumbuhan bakteri penyebab infeksi.",
            "Membantu tubuh melawan infeksi."

        ],
        "processing": [
        {
        "disease": "Nafsu Makan Sangat Menurun",
        "recipe": "Lempuyang direbus bersama sedikit gula aren dan diminum sebelum makan."
        },
        {
        "disease": "Perut Terasa Tidak Nyaman",
        "recipe": "Iris tipis lempuyang, rebus bersama daun jeruk selama 10 menit."
        },
        {
        "disease": "Saat Tubuh Terasa Panas Dingin",
        "recipe": "Lempuyang direbus bersama jahe dan serai menjadi minuman herbal hangat."
        }
        ]

    },


    "Lengkuas": {

        "scientific_name":
            "Alpinia galanga",

        "benefits": [

            "Membantu mengurangi oksidasi kolesterol.",
            "Membantu tubuh melawan infeksi secara lebih efektif.",
            "Mendukung kesehatan berbagai organ tubuh."

        ],
        "processing": [
        { 
        "disease": "Pegal Setelah Aktivitas Fisik",
        "recipe": "Lengkuas diparut dan dicampur minyak kelapa, kemudian digunakan sebagai baluran tradisional."
        },
        {
        "disease": "Masuk Angin Akut",
        "recipe": "Lengkuas direbus bersama serai dan jahe selama 15 menit."
        },
        {
        "disease": "Perut Terasa Kembung",
        "recipe": "Air rebusan lengkuas diminum hangat setelah makan."
        }
        ]

    },


    "Temu Hitam": {

        "scientific_name":
            "Curcuma aeruginosa",

        "benefits": [

            "Memicu apoptosis (kematian sel abnormal).",
            "Membantu menjaga fungsi memori dan konsentrasi.",
            "Membantu mengurangi peradangan kronis pada tubuh.."

        ],
        "processing": [
        {
        "disease": "Keluhan Saluran Pencernaan",
        "recipe": "Temu hitam direbus bersama daun salam dan diminum hangat."
        },
        {
        "disease": "Batuk Lumayan Parah",
        "recipe": "Temu hitam dipotong kecil lalu direbus bersama madu dan jahe."
        },
        {
        "disease": "Tubuh Terasa Kurang Fit Dan Lelah",
        "recipe": "Temu hitam direbus bersama temulawak sebagai jamu tradisional."
        }
        ]

    },


    "Temu Kunci": {

        "scientific_name":
            "Boesenbergia rotunda",

        "benefits": [

            "Membantu mencegah infeksi kronis.",
            "Membantu mengurangi plak gigi.",
            "Membantu menjaga kadar gula darah tetap stabil."

        ],
        "processing": [
        {
        "disease": "Perut Kembung ",
        "recipe": "Temu kunci diiris tipis lalu direbus selama 15 menit hingga air beraroma khas."
        },
        { 
        "disease": "Pemanfaatan untuk Ibu Menyusui",
        "recipe": "Temu kunci dimasak bersama daun katuk sebagai ramuan tradisional pendamping makanan."
        },
        {
        "disease": "Gangguan Pencernaan Akut",
        "recipe": "Air rebusan temu kunci diminum setelah makan."
        }
        ]
    },


    "Temulawak": {

        "scientific_name":
            "Curcuma xanthorrhiza",

        "benefits": [

            "Mengurangi stres oksidatif pada jaringan ginjal sehingga mendukung fungsi ginjal.",
            "Mendukung metabolisme karbohidrat.",
            "Melindungi sistem saraf dari stres oksidatif."

        ],
        "processing": [
        {
        "disease": "Menjaga Fungsi Hati",
        "recipe": "Temulawak dipotong tipis lalu direbus bersama 500 ml air hingga tersisa sekitar satu gelas."
        },
        {
        "disease": "Nafsu Makan Menurun",
        "recipe": "Temulawak direbus bersama madu dan sedikit gula aren menjadi minuman herbal."
        },
        {
        "disease": "Keluhan Pada Pencernaan",
        "recipe": "Temulawak direbus bersama kunyit dan daun pandan selama 15 menit."
        }
        ]

    }
}


# ============================================================
# TRANSFORM (SAMA DENGAN TRAINING MODEL)
# ============================================================

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# ============================================================
# PREPROCESSING GAMBAR (TAMBAHKAN DI SINI)
# ============================================================

# ============================================================
# PREPROCESSING GAMBAR
# ============================================================

def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")
    image = ImageOps.exif_transpose(image)
    tensor = transform(image)
    tensor = tensor.unsqueeze(0)
    tensor = tensor.to(DEVICE)

    return tensor

# ============================================================
# MODEL HYBRID RESNET50 + ViT (SAMA DENGAN NOTEBOOK TRAINING)
# ============================================================

FUSION_FEATURES = 2048 + 768  # 2816

class HybridResNetViTBaseline(nn.Module):

    def __init__(self, num_classes=10):

        super().__init__()

        # Backbone ResNet-50
        self.resnet = resnet50(weights=None)
        self.resnet.fc = nn.Identity()

        # Backbone ViT-B/16
        self.vit = vit_b_16(weights=None)
        self.vit.heads = nn.Identity()

        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(FUSION_FEATURES, 512),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):

        resnet_features = self.resnet(x)
        vit_features = self.vit(x)

        combined = torch.cat(
            (resnet_features, vit_features),
            dim=1
        )

        return self.classifier(combined)


        # ----------------------------------------------------
        # VIT-B/16
        # ----------------------------------------------------

        self.vit = vit_b_16(
            weights=None
        )

        self.vit.heads = nn.Identity()


        # ----------------------------------------------------
        # CLASSIFIER
        #
        # ResNet = 2048
        # ViT    = 768
        #
        # Total  = 2816
        # ----------------------------------------------------

        self.classifier = nn.Sequential(

            nn.Linear(
                2816,
                512
            ),

            nn.ReLU(),

            nn.Dropout(
                0.3
            ),

            nn.Linear(
                512,
                num_classes
            )

        )


    # ========================================================
    # FEATURE
    # ========================================================

    def extract_features(
        self,
        x
    ):

        resnet_features = self.resnet(
            x
        )

        vit_features = self.vit(
            x
        )

        features = torch.cat(

            [
                resnet_features,
                vit_features
            ],

            dim=1

        )

        return features


    # ========================================================
    # FORWARD
    # ========================================================

    def forward(
        self,
        x
    ):

        features = self.extract_features(
            x
        )

        return self.classifier(
            features
        )


# ============================================================
# GLOBAL MODEL
# ============================================================

model = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    global model


    print()
    print("=" * 70)
    print("RIMPANG AI - MEMUAT MODEL")
    print("=" * 70)


    print()
    print("Model:")
    print(MODEL_PATH)


    print()
    print("Device:")
    print(DEVICE)


    # --------------------------------------------------------
    # CEK MODEL
    # --------------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(

            "File model tidak ditemukan:\n"
            + str(MODEL_PATH)

        )


    # --------------------------------------------------------
    # BUAT MODEL
    # --------------------------------------------------------

    print()
    print(
        "Membuat Hybrid ResNet-50 + ViT-B/16..."
    )


    model = HybridResNetViTBaseline(
        num_classes=NUM_CLASSES
    )


    # --------------------------------------------------------
    # LOAD CHECKPOINT
    # --------------------------------------------------------

    print()
    print(
        "Memuat checkpoint..."
    )


    checkpoint = torch.load(

        MODEL_PATH,

        map_location=DEVICE,

        weights_only=True

    )


    # --------------------------------------------------------
    # CHECKPOINT HARUS STATE DICT
    # --------------------------------------------------------

    if not isinstance(
        checkpoint,
        dict
    ):

        raise RuntimeError(
            "Format checkpoint model tidak valid."
        )


    # --------------------------------------------------------
    # CLEAN MODULE PREFIX
    # --------------------------------------------------------

    cleaned_state = {}


    for key, value in checkpoint.items():

        if key.startswith(
            "module."
        ):

            key = key[
                len("module.") :
            ]


        cleaned_state[
            key
        ] = value


    # --------------------------------------------------------
    # LOAD STATE
    # --------------------------------------------------------

    try:

        model.load_state_dict(

            cleaned_state,

            strict=True

        )

    except RuntimeError as error:

        print()
        print("=" * 70)
        print("ERROR LOAD MODEL")
        print("=" * 70)
        print(error)
        print()

        raise

     # --------------------------------------------------------
    # DEVICE
    # --------------------------------------------------------

    model = model.to(DEVICE)
    model.eval()

    print("Model device :", next(model.parameters()).device)
    print("Tensor device:", DEVICE)

    # --------------------------------------------------------
    # INFO MODEL
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("MODEL BERHASIL DIMUAT")
    print("=" * 70)

    print()
    print("Arsitektur : Hybrid ResNet-50 + ViT-B/16")
    print("Feature    : 2816")
    print("Classifier : 2816 -> 512 -> 10")
    print("Device     :", DEVICE)
    print("Kelas      :", NUM_CLASSES)
    print()

    for number, name in enumerate(CLASS_NAMES, start=1):
        print(f"{number:02d}. {name}")

    print()
    print("=" * 70)
    print()

    return model

    # ============================================================
    # CEK EXTENSION
    # ============================================================

def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


# ============================================================
# PREDICT IMAGE
# ============================================================

def predict_image(image):

    # --------------------------------------------------------
    # UBAH KE RGB
    # --------------------------------------------------------

    image = image.convert("RGB")

    # --------------------------------------------------------
    # PREPROCESSING
    # --------------------------------------------------------

    tensor = transform(image)
    tensor = tensor.unsqueeze(0)

    # Pindahkan tensor ke device yang sama dengan model
    tensor = tensor.to(next(model.parameters()).device)

    # --------------------------------------------------------
    # PREDIKSI
    # --------------------------------------------------------

    with torch.no_grad():

        print("Tensor device :", tensor.device)
        print("Model device  :", next(model.parameters()).device)

        output = model(tensor)

        probabilities = torch.softmax(output, dim=1)

        confidence, predicted = torch.max(probabilities, dim=1)

    # --------------------------------------------------------
    # HASIL
    # --------------------------------------------------------

    predicted_class = CLASS_NAMES[predicted.item()]
    confidence_score = confidence.item() * 100

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model(
            tensor
        )


        probabilities = torch.softmax(

            logits,

            dim=1

        )


        confidence, index = torch.max(

            probabilities,

            dim=1

        )


    # --------------------------------------------------------
    # INDEX
    # --------------------------------------------------------

    predicted_index = (
        index.item()
    )


    # --------------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------------

    confidence_value = (

        confidence.item()
        * 100.0

    )


    # --------------------------------------------------------
    # CLASS
    # --------------------------------------------------------

    prediction = CLASS_NAMES[
        predicted_index
    ]
    # ============================================================
    # AMBIL INFORMASI TANAMAN
    # ============================================================

    info = PLANT_INFO.get(
    prediction,
    {
        "scientific_name": "-",
        "benefits": []
    }
    )

    # --------------------------------------------------------
    # TOP 3
    # --------------------------------------------------------

    top_count = min(
        3,
        NUM_CLASSES
    )


    values, indices = torch.topk(

        probabilities[0],

        k=top_count

    )


    top_predictions = []


    for value, class_index in zip(

        values.tolist(),

        indices.tolist()

    ):

        top_predictions.append({

            "class":
                CLASS_NAMES[
                    class_index
                ],

            "confidence":
                round(
                    value * 100.0,
                    2
                )

        })


    # --------------------------------------------------------
    # INFO TANAMAN
    # --------------------------------------------------------

    plant_info = PLANT_INFO.get(

        prediction,

        {

            "scientific_name":
                "-",

            "benefits":
                []

        }

    )


    return {

        "prediction":
            prediction,

        "confidence":
            round(
                confidence_value,
                2
            ),

        "scientific_name":
            plant_info[
                "scientific_name"
            ],

        "benefits":
            plant_info[
                "benefits"
            ],

        "top_predictions":
            top_predictions

    }


# ============================================================
# HOME
# ============================================================

@app.route("/")
def index():

    return render_template(

        "index.html",

        class_names=CLASS_NAMES

    )

# ============================================================
# PREDICT
# ============================================================

# ============================================================
# PREDICT GAMBAR
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:
        top_predictions = []

        # ==========================
        # CEK FILE
        # ==========================
        if "image" not in request.files:

            return jsonify({
                "success": False,
                "message": "Gambar belum dipilih."
            }), 400

        file = request.files["image"]

        if file.filename == "":

            return jsonify({
                "success": False,
                "message": "Gambar belum dipilih."
            }), 400

        if not allowed_file(file.filename):

            return jsonify({
                "success": False,
                "message": "Format gambar harus JPG, JPEG, PNG, atau WEBP."
            }), 400

        # ==========================
        # SIMPAN FILE
        # ==========================
        filename = secure_filename(file.filename)

        file_path = UPLOAD_FOLDER / filename

        file.save(file_path)

        # ==========================
        # PREPROCESSING GAMBAR
        # ==========================

        try:

            image = preprocess_image(file_path)

        except Exception:

            file_path.unlink(missing_ok=True)

            return jsonify({
                "success": False,
                "message": (
                    "File bukan gambar yang valid atau rusak. "
                    "Gunakan foto JPG, PNG, atau WEBP asli."
                )
            }), 400

        # PINDAHKAN GAMBAR KE DEVICE YANG SAMA DENGAN MODEL
        image = image.to(next(model.parameters()).device)

        print("Image device :", image.device)
        print("Model device :", next(model.parameters()).device)
        print("Image dtype  :", image.dtype)
        print("Model dtype  :", next(model.parameters()).dtype)

        # ==========================
        # PREDIKSI MODEL
        # ==========================

        with torch.no_grad():

            output = model(image)

            print("\n========== OUTPUT MENTAH ==========")
            print(output)
            print("==================================")

            probabilities = torch.softmax(output, dim=1)

            print("\n========== PROBABILITAS ==========")
            print(probabilities)
            print("=================================")

            confidence, predicted = torch.max(probabilities, dim=1)

        prediction = CLASS_NAMES[predicted.item()]
        confidence = round(confidence.item() * 100, 2)

        # ==========================
        # SINYAL DETEKSI NON-RIMPANG
        # ==========================
        # Energy  = logsumexp(logits). Gambar di luar
        #           distribusi menghasilkan logits kecil
        #           sehingga energy rendah.
        # Entropy = ketidakpastian sebaran probabilitas
        #           (0 = yakin, 1 = ragu merata).

        energy_score = torch.logsumexp(
            output[0],
            dim=0
        ).item()

        probs_vector = probabilities[0]

        entropy_score = float(
            -(
                probs_vector
                * torch.log(probs_vector + 1e-12)
            ).sum().item()
            / math.log(NUM_CLASSES)
        )

        # ==========================
        # TOP 3 PREDIKSI
        # ==========================

        values, indices = torch.topk(probabilities[0], k=3)

        top_predictions.clear()

        for value, idx in zip(values, indices):
            top_predictions.append({
                "class": CLASS_NAMES[idx.item()],
                "confidence": round(value.item() * 100, 2)
            })
        print("\n================ DEBUG MODEL ================")
        print("Index Prediksi :", predicted.item())
        print("Nama Prediksi  :", prediction)
        print("Confidence      :", confidence)

        values, indices = torch.topk(probabilities[0], k=10)

        print("\nTOP 10 PREDIKSI MODEL")

        for i, (v, idx) in enumerate(zip(values, indices)):
            print(
                f"{i+1}. {CLASS_NAMES[idx.item()]} : {v.item()*100:.2f}%"
    )

        print("=============================================\n")

        # Batasi confidence agar tidak terlalu overconfident
        if confidence > 98:
            confidence = 97.85

        # ==========================
        # GERBANG NON-RIMPANG (OOD)
        # ==========================
        # Hasil kalibrasi pada 150 gambar test valid
        # vs 20 gambar bukan rimpang (chart, drawing,
        # noise, warna polos):
        # - energy : valid p1 = 2.57 (median 3.97),
        #            bukan rimpang maks 2.68
        # - entropy: valid p95 = 0.56,
        #            bukan rimpang mayoritas > 0.70

        ENERGY_MIN = 2.75
        ENTROPY_MAX = 0.68

        is_out_of_distribution = (
            energy_score < ENERGY_MIN
            or entropy_score > ENTROPY_MAX
        )

        print("Energy   :", round(energy_score, 3))
        print("Entropy  :", round(entropy_score, 3))
        print("OOD      :", is_out_of_distribution)

        if is_out_of_distribution:

            return jsonify({

                "success": True,

                "prediction": "Bukan Tanaman Rimpang",

                "confidence": confidence,

                "message": (
                    "Gambar tidak dikenali sebagai tanaman "
                    "rimpang. Pastikan foto menampilkan "
                    "rimpang secara jelas dan dekat."
                ),

                "scientific_name": "-",

                "benefits": [],

                "processing": [],

                "top_predictions": top_predictions

            })

        # ==========================
        # BATAS CONFIDENCE
        # ==========================
        # Tiga zona hasil:
        # 1. DIKENALI   : conf >= 70%.
        # 2. KEMUNGKINAN: conf >= 35% dan unggul 1.5x
        #    dari kandidat kedua -> tampilkan sebagai
        #    "Kemungkinan: <kelas>" (keyakinan rendah).
        # 3. DITOLAK    : selain itu.

        MIN_CONFIDENCE = 70
        POSSIBLE_CONFIDENCE = 35
        POSSIBLE_RATIO = 1.5

        second_confidence = (
            top_predictions[1]["confidence"]
            if len(top_predictions) > 1
            else 0.0
        )

        is_recognized = (
            confidence >= MIN_CONFIDENCE
        )

        is_possible = (
            not is_recognized
            and confidence >= POSSIBLE_CONFIDENCE
            and confidence >= (
                POSSIBLE_RATIO * second_confidence
            )
        )

        if is_possible:

            possible_info = PLANT_INFO.get(
                prediction,
                {
                    "scientific_name": "-",
                    "benefits": [],
                    "processing": []
                }
            )

            return jsonify({

                "success": True,

                "prediction": f"Kemungkinan: {prediction}",

                "confidence": confidence,

                "message": (
                    "Keyakinan AI rendah. Hasil ini perkiraan "
                    "terbaik - gunakan foto rimpang yang lebih "
                    "dekat dan jelas untuk hasil pasti."
                ),

                "scientific_name": possible_info["scientific_name"],

                "benefits": possible_info["benefits"],

                "processing": possible_info["processing"],

                "top_predictions": top_predictions

    })

        if not is_recognized:

            return jsonify({

                "success": True,

                "prediction": "Tanaman Tidak Dikenali",

                "confidence": confidence,

                "message": "Confidence terlalu rendah. Gunakan foto yang lebih jelas.",

                "scientific_name": "-",

                "benefits": [],

                "processing": [],

                "top_predictions": top_predictions

    })

        # ==========================
        # AMBIL INFORMASI TANAMAN
        # ==========================
        plant_info = PLANT_INFO.get(
            prediction,
            {
        "scientific_name": "-",
        "benefits": [],
        "processing": []
            }
        )

        # ==========================
        # TOP 3 PREDIKSI
        # ==========================
        values, indices = torch.topk(probabilities, k=3)

        top_predictions = []

        for value, index in zip(values[0], indices[0]):

            top_predictions.append({

                "class": CLASS_NAMES[index.item()],

                "confidence": round(value.item() * 100, 2)
            })


        # ==========================
        # LOG TERMINAL
        # ==========================
        print("-" * 60)
        print("Gambar      :", filename)
        print("Prediksi    :", prediction)
        print("Confidence  :", confidence, "%")
        print("Nama ilmiah :", plant_info["scientific_name"])
        print("-" * 60)

        # ==========================
        # RESPONSE KE WEBSITE
        # ==========================

        print("PREDIKSI :", prediction)
        print("PROCESSING :", plant_info.get("processing"))
        print("BENEFITS :", plant_info.get("benefits"))
        
        return jsonify({

    "success": True,

    "prediction": prediction,

    "confidence": confidence,

    "message": "Tanaman berhasil diidentifikasi.",

    "scientific_name": plant_info["scientific_name"],

    "benefits": plant_info["benefits"],

    # WAJIB ADA
    "processing": plant_info["processing"],

    "top_predictions": top_predictions,

    "filename": filename

})


    except RequestEntityTooLarge:

        return jsonify({
        "success": False,
        "message": "Ukuran gambar maksimal 10 MB."
    }), 413

    except Exception:
        print("\n========== ERROR PREDICT ==========")
        traceback.print_exc()
        print("===================================\n")

        return jsonify({
        "success": False,
        "message": "Terjadi kesalahan saat memproses gambar. Silakan coba lagi."
    }), 500


# ============================================================
# FILE TERLALU BESAR
# ============================================================

@app.errorhandler(413)
def file_terlalu_besar(error):

    return jsonify({
        "success": False,
        "message": "Ukuran gambar maksimal 10 MB."
    }), 413


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():

    return jsonify({

        "success":
            True,

        "application":
            "RIMPANG AI",

        "mode":
            "WEB",

        "realtime":
            False,

        "model":
            "Hybrid ResNet-50 + ViT-B/16",

        "model_file":
            MODEL_PATH.name,

        "device":
            str(DEVICE),

        "num_classes":
            NUM_CLASSES,

        "classes":
            CLASS_NAMES

    })


# ============================================================
# ERROR FILE TERLALU BESAR
# ============================================================

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({

        "success":
            False,

        "message":
            "Ukuran gambar maksimal 10 MB."

    }), 413


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    load_model()


    print()
    print("=" * 70)
    print("RIMPANG AI - WEB IDENTIFICATION")
    print("=" * 70)

    print()
    print(
        "Server:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()

    print(
        "Mode: WEB"
    )

    print(
        "Webcam: TIDAK DIGUNAKAN"
    )

    print()
    print("=" * 70)
    print()


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )