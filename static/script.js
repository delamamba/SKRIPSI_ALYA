/* ============================================================
   RIMPANG AI
   WEB IDENTIFICATION
   ============================================================

   Tugas JavaScript:
   - memilih gambar
   - preview gambar
   - upload gambar
   - mengirim gambar ke Flask
   - menerima hasil model
   - menampilkan hasil identifikasi

   MODEL DAN DATA KHASIAT TIDAK DITULIS DI SINI.
   Model berada di app.py.
============================================================ */


/* ============================================================
   ELEMENT HTML
============================================================ */

const imageInput =
    document.getElementById("imageInput");

const chooseButton =
    document.getElementById("chooseButton");

const uploadArea =
    document.getElementById("uploadArea");

const previewContainer =
    document.getElementById("previewContainer");

const previewImage =
    document.getElementById("previewImage");

const fileName =
    document.getElementById("fileName");

const removeImage =
    document.getElementById("removeImage");

const identifyButton =
    document.getElementById("identifyButton");

const resultName =
    document.getElementById("resultName");

const resultMessage =
    document.getElementById("resultMessage");

const confidenceValue =
    document.getElementById("confidenceValue");

const confidenceBar =
    document.getElementById("confidenceBar");

const statusText =
    document.getElementById("statusText");

const scientificName =
    document.getElementById("scientificName");

const infoScientificName =
    document.getElementById("infoScientificName");

const benefitsList =
    document.getElementById("benefitsList");

const topPredictions =
    document.getElementById("topPredictions");


/* ============================================================
   CEK ELEMENT
============================================================ */

console.log(
    "RIMPANG AI - script.js berhasil dimuat."
);

console.log(
    "imageInput:",
    imageInput
);

console.log(
    "identifyButton:",
    identifyButton
);

console.log(
    "resultName:",
    resultName
);

console.log(
    "scientificName:",
    scientificName
);

console.log(
    "benefitsList:",
    benefitsList
);

console.log(
    "topPredictions:",
    topPredictions
);


/* ============================================================
   PILIH GAMBAR
============================================================ */

if (chooseButton && imageInput) {

    chooseButton.addEventListener(
        "click",
        function () {

            imageInput.click();

        }
    );

}


/* ============================================================
   INPUT FILE
============================================================ */

if (imageInput) {

    imageInput.addEventListener(
        "change",
        function () {

            if (
                !this.files ||
                !this.files.length
            ) {

                return;

            }

            processImage(
                this.files[0]
            );

        }
    );

}


/* ============================================================
   DRAG OVER
============================================================ */

if (uploadArea) {

    uploadArea.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            uploadArea.classList.add(
                "dragover"
            );

        }
    );


    /* ========================================================
       DRAG LEAVE
    ======================================================== */

    uploadArea.addEventListener(
        "dragleave",
        function () {

            uploadArea.classList.remove(
                "dragover"
            );

        }
    );


    /* ========================================================
       DROP
    ======================================================== */

    uploadArea.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            uploadArea.classList.remove(
                "dragover"
            );


            const files =
                event.dataTransfer.files;


            if (
                !files ||
                !files.length
            ) {

                return;

            }


            processImage(
                files[0]
            );

        }
    );

}


/* ============================================================
   PROSES GAMBAR
============================================================ */

function processImage(file) {

    if (!file) {

        return;

    }


    /* --------------------------------------------------------
       FORMAT YANG DIIZINKAN
    -------------------------------------------------------- */

    const allowedTypes = [

        "image/jpeg",

        "image/png",

        "image/webp"

    ];


    if (
        !allowedTypes.includes(
            file.type
        )
    ) {

        alert(
            "Format gambar harus JPG, JPEG, PNG, atau WEBP."
        );


        if (imageInput) {

            imageInput.value = "";

        }


        return;

    }


    /* --------------------------------------------------------
       FILE MAKSIMAL 10 MB
    -------------------------------------------------------- */

    const maxSize =
        10 * 1024 * 1024;


    if (
        file.size > maxSize
    ) {

        alert(
            "Ukuran gambar maksimal 10 MB."
        );


        if (imageInput) {

            imageInput.value = "";

        }


        return;

    }


    /* --------------------------------------------------------
       BACA GAMBAR
    -------------------------------------------------------- */

    const reader =
        new FileReader();


    reader.onload =
        function (event) {


            if (previewImage) {

                previewImage.src =
                    event.target.result;

            }


            if (previewContainer) {

                previewContainer.style.display =
                    "block";

            }


            if (uploadArea) {

                uploadArea.style.display =
                    "none";

            }


            if (fileName) {

                fileName.textContent =
                    file.name;

            }


            if (identifyButton) {

                identifyButton.disabled =
                    false;

            }


            resetResult();


            if (statusText) {

                statusText.textContent =
                    "Gambar siap diidentifikasi.";

            }

        };


    reader.onerror =
        function () {

            alert(
                "Gambar tidak dapat dibaca."
            );

        };


    reader.readAsDataURL(
        file
    );

}


/* ============================================================
   HAPUS GAMBAR
============================================================ */

if (removeImage) {

    removeImage.addEventListener(
        "click",
        function () {

            clearImage();

        }
    );

}


/* ============================================================
   CLEAR IMAGE
============================================================ */

function clearImage() {


    if (imageInput) {

        imageInput.value = "";

    }


    if (previewImage) {

        previewImage.src = "";

    }


    if (previewContainer) {

        previewContainer.style.display =
            "none";

    }


    if (uploadArea) {

        uploadArea.style.display =
            "block";

    }


    if (identifyButton) {

        identifyButton.disabled =
            true;

    }


    resetResult();


    if (statusText) {

        statusText.textContent =
            "Menunggu gambar.";

    }

}


/* ============================================================
   RESET HASIL
============================================================ */

function resetResult() {


    hasIdentificationResult = false;

    refreshNavigationLocks();


    if (resultName) {

        resultName.textContent =
            "Belum Ada Hasil";

    }


    if (resultMessage) {

        resultMessage.textContent =
            "Silakan pilih gambar tanaman terlebih dahulu.";

    }


    if (confidenceValue) {

        confidenceValue.textContent =
            "0.00%";

    }


    if (confidenceBar) {

        confidenceBar.style.width =
            "0%";

    }


    if (scientificName) {

        scientificName.textContent =
            "-";

    }


    if (infoScientificName) {

        infoScientificName.textContent =
            "-";

    }


    if (benefitsList) {

        benefitsList.innerHTML = `

            <li>
                Hasil khasiat akan ditampilkan
                setelah proses identifikasi.
            </li>

        `;

    }


    if (topPredictions) {

        topPredictions.innerHTML = `

            <div class="top-prediction-empty">
                Belum ada hasil prediksi.
            </div>

        `;

    }

}


/* ============================================================
   IDENTIFIKASI GAMBAR
============================================================ */

if (identifyButton) {

    identifyButton.addEventListener(
        "click",
        identifyImage
    );

}


/* ============================================================
   FUNGSI IDENTIFIKASI
============================================================ */

async function identifyImage() {


    /* --------------------------------------------------------
       CEK GAMBAR
    -------------------------------------------------------- */

    if (
        !imageInput ||
        !imageInput.files ||
        !imageInput.files.length
    ) {

        alert(
            "Silakan pilih gambar terlebih dahulu."
        );

        return;

    }


    const file =
        imageInput.files[0];


    /* --------------------------------------------------------
       LOADING
    -------------------------------------------------------- */

    identifyButton.disabled =
        true;


    identifyButton.classList.add(
        "loading"
    );


    const buttonText =
        identifyButton.querySelector(
            "span:first-child"
        );


    if (buttonText) {

        buttonText.textContent =
            "Menganalisis gambar...";

    }


    if (resultName) {

        resultName.textContent =
            "Menganalisis...";

    }


    if (resultMessage) {

        resultMessage.textContent =
            "Model Hybrid ResNet-50 + ViT-B/16 sedang memproses gambar.";

    }


    if (confidenceValue) {

        confidenceValue.textContent =
            "0.00%";

    }


    if (confidenceBar) {

        confidenceBar.style.width =
            "0%";

    }


    if (statusText) {

        statusText.textContent =
            "Model sedang bekerja...";

    }


    try {


        /* ----------------------------------------------------
           FORM DATA
        ---------------------------------------------------- */

        const formData =
            new FormData();


        formData.append(
            "image",
            file
        );


        /* ----------------------------------------------------
           KIRIM KE FLASK
        ---------------------------------------------------- */

        console.log(
            "Mengirim gambar ke /predict..."
        );


        const response =
            await fetch(
                "/predict",
                {
                    method:
                        "POST",

                    body:
                        formData
                }
            );


        /* ----------------------------------------------------
           BACA RESPONSE
        ---------------------------------------------------- */

        const data =
            await response.json();


        console.log(
            "Response server:",
            data
        );


        /* ----------------------------------------------------
           CEK RESPONSE
        ---------------------------------------------------- */

        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(

                data.message ||
                "Gagal melakukan identifikasi."

            );

        }


        /* ----------------------------------------------------
           TAMPILKAN HASIL
        ---------------------------------------------------- */

        showResult(
            data
        );


        /* ----------------------------------------------------
           PINDAH KE HALAMAN HASIL
        ---------------------------------------------------- */

        goToPage(
            "page-hasil"
        );

    }


    catch (error) {

        console.error(
            "ERROR IDENTIFIKASI:",
            error
        );


        showError(
            error.message
        );


        goToPage(
            "page-hasil"
        );

    }


    finally {


        identifyButton.disabled =
            false;


        identifyButton.classList.remove(
            "loading"
        );


        if (buttonText) {

            buttonText.textContent =
                "Identifikasi Gambar";

        }

    }

}


/* ============================================================
   TAMPILKAN HASIL
============================================================ */

function showResult(data) {


    console.log(
        "HASIL IDENTIFIKASI:",
        data
    );


    /* --------------------------------------------------------
       HALAMAN HASIL & KHASIAT SUDAH TERISI
    -------------------------------------------------------- */

    hasIdentificationResult = true;

    refreshNavigationLocks();

    const isUnknown =
        data.prediction ===
            "Tanaman Tidak Dikenali" ||
        data.prediction ===
            "Bukan Tanaman Rimpang";


    /* --------------------------------------------------------
       FOTO YANG DIUNGGAH TAMPIL DI HALAMAN HASIL
    -------------------------------------------------------- */

    const resultImage =
        document.getElementById("resultImage");


    if (
        resultImage &&
        previewImage &&
        previewImage.src
    ) {

        resultImage.src =
            previewImage.src;

    }


    /* --------------------------------------------------------
       NAMA TANAMAN
    -------------------------------------------------------- */

    if (resultName) {

        resultName.textContent =
            data.prediction ||
            "Tanaman Tidak Dikenali";

    }


    /* --------------------------------------------------------
       PESAN
    -------------------------------------------------------- */

    if (resultMessage) {

        resultMessage.textContent =
            data.message ||
            "Tanaman berhasil diidentifikasi oleh model.";

    }


    /* --------------------------------------------------------
       CONFIDENCE
    -------------------------------------------------------- */

    const confidence =
        Number(
            data.confidence || 0
        );


    if (confidenceValue) {

        confidenceValue.textContent =
            confidence.toFixed(2) + "%";

    }


    if (confidenceBar) {

        const safeConfidence =
            Math.max(
                0,
                Math.min(
                    100,
                    confidence
                )
            );


        confidenceBar.style.width =
            safeConfidence + "%";

    }


    /* --------------------------------------------------------
       NAMA ILMIAH
    -------------------------------------------------------- */

    if (scientificName) {

        scientificName.textContent =
            data.scientific_name ||
            "-";

    }


    if (infoScientificName) {

        infoScientificName.textContent =
            data.scientific_name ||
            "-";

    }


    /* --------------------------------------------------------
       KHASIAT
    -------------------------------------------------------- */

    showBenefits(
        data.benefits
    );

    /* --------------------------------------------------------
       CARA PENGOLAHAN
    -------------------------------------------------------- */

    showProcessing(data.processing);


    /* --------------------------------------------------------
       TOP 3
    -------------------------------------------------------- */

    showTopPredictions(
        data.top_predictions
    );


    /* --------------------------------------------------------
       STATUS
    -------------------------------------------------------- */

    if (statusText) {

        statusText.textContent =
            isUnknown
                ? "Tanaman belum dapat dikenali."
                : "Tanaman berhasil teridentifikasi.";

    }


    console.log(
        "Hasil berhasil ditampilkan."
    );

}


/* ============================================================
   TAMPILKAN KHASIAT
============================================================ */

function showBenefits(
    benefits
) {


    if (!benefitsList) {

        console.warn(
            "Element #benefitsList tidak ditemukan."
        );

        return;

    }


    benefitsList.innerHTML =
        "";


    if (
        Array.isArray(
            benefits
        ) &&
        benefits.length > 0
    ) {


        benefits.forEach(
            function (benefit) {


                const li =
                    document.createElement(
                        "li"
                    );


                li.textContent =
                    benefit;


                benefitsList.appendChild(
                    li
                );

            }
            
        );

    


        return;

    }


    const li =
        document.createElement(
            "li"
        );


    li.textContent =
        "Informasi pemanfaatan belum tersedia.";


    benefitsList.appendChild(
        li
    );

}
/* ============================================================
   TAMPILKAN CARA PENGOLAHAN
============================================================ */

function showProcessing(processing) {

    if (!processingList) return;

    processingList.innerHTML = "";

    if (Array.isArray(processing) && processing.length > 0) {

        processing.forEach(function(item, index) {

            const div = document.createElement("div");
            div.className = "processing-item";

            div.innerHTML = `
                <strong>💊 Pengolahan ${index + 1}</strong>
                <p><b>Penyakit:</b> ${item.disease}</p>
                <p>${item.recipe}</p>
            `;

            processingList.appendChild(div);
        });

        return;
    }

    processingList.innerHTML = `
        <div class="processing-item">
            Cara pengolahan belum tersedia.
        </div>
    `;
}


/* ============================================================
   TOP 3 PREDIKSI
============================================================ */

function showTopPredictions(
    predictions
) {


    if (!topPredictions) {

        console.warn(
            "Element #topPredictions tidak ditemukan."
        );

        return;

    }


    topPredictions.innerHTML =
        "";


    if (
        !Array.isArray(
            predictions
        ) ||
        predictions.length === 0
    ) {


        topPredictions.innerHTML = `

            <div class="top-prediction-empty">
                Tidak ada data prediksi.
            </div>

        `;


        return;

    }


    predictions.forEach(
        function (
            item,
            index
        ) {


            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "top-prediction-row";


            const rank =
                document.createElement(
                    "div"
                );


            rank.className =
                "top-prediction-rank";


            rank.textContent =
                index + 1;


            const name =
                document.createElement(
                    "div"
                );


            name.className =
                "top-prediction-name";


            name.textContent =
                item.class ||
                "-";


            const predictionConfidence =
                document.createElement(
                    "div"
                );


            predictionConfidence.className =
                "top-prediction-confidence";


            predictionConfidence.textContent =
                Number(
                    item.confidence || 0
                ).toFixed(2)
                + "%";


            row.appendChild(
                rank
            );


            row.appendChild(
                name
            );


            row.appendChild(
                predictionConfidence
            );


            topPredictions.appendChild(
                row
            );

        }
    );

}


/* ============================================================
   TAMPILKAN ERROR
============================================================ */

function showError(
    message
) {


    hasIdentificationResult = true;

    refreshNavigationLocks();


    if (resultName) {

        resultName.textContent =
            "Terjadi Kesalahan";

    }


    if (resultMessage) {

        resultMessage.textContent =
            message ||
            "Identifikasi gagal dilakukan.";

    }


    if (confidenceValue) {

        confidenceValue.textContent =
            "0.00%";

    }


    if (confidenceBar) {

        confidenceBar.style.width =
            "0%";

    }


    if (scientificName) {

        scientificName.textContent =
            "-";

    }


    if (infoScientificName) {

        infoScientificName.textContent =
            "-";

    }


    if (benefitsList) {

        benefitsList.innerHTML = `

            <li>
                Identifikasi tidak dapat dilakukan.
            </li>

        `;

    }


    if (topPredictions) {

        topPredictions.innerHTML = `

            <div class="top-prediction-empty">
                Tidak ada hasil prediksi.
            </div>

        `;

    }


    if (statusText) {

        statusText.textContent =
            "Proses gagal.";

    }

}


/* ============================================================
   NAVIGASI HALAMAN (SLIDE)

   Urutan halaman:
   1. Beranda
   2. Upload
   3. Hasil Identifikasi
   4. Informasi Khasiat
   5. Data Klasifikasi
============================================================ */

const PAGE_ORDER = [

    "page-beranda",
    "page-upload",
    "page-hasil",
    "page-khasiat",
    "page-klasifikasi"

];


const PAGE_HASHES = {

    "page-beranda": "beranda",
    "page-upload": "upload",
    "page-hasil": "hasil",
    "page-khasiat": "khasiat",
    "page-klasifikasi": "klasifikasi"

};


const navLinks =
    document.querySelectorAll(".nav-link");

const pagerPrev =
    document.getElementById("pagerPrev");

const pagerNext =
    document.getElementById("pagerNext");

const pagerDots =
    document.getElementById("pagerDots");


let currentPageIndex = 0;


/* Halaman hasil & khasiat baru terbuka setelah
   gambar diunggah dan diidentifikasi */

let hasIdentificationResult = false;


/* ============================================================
   AKSES HALAMAN
============================================================ */

function canAccessPage(pageId) {

    if (
        pageId === "page-hasil" ||
        pageId === "page-khasiat"
    ) {

        return hasIdentificationResult;

    }


    return true;

}


/* ============================================================
   PINDAH HALAMAN
============================================================ */

function goToPage(pageId, animate) {

    const targetIndex =
        PAGE_ORDER.indexOf(pageId);


    if (targetIndex === -1) {

        return;

    }


    /* --------------------------------------------------------
       HALAMAN TERKUNCI JIKA BELUM TERISI
    -------------------------------------------------------- */

    if (!canAccessPage(pageId)) {

        showNavigationHint();

        return;

    }


    const useAnimation =
        animate !== false;


    const direction =
        targetIndex >= currentPageIndex
            ? "slide-in-right"
            : "slide-in-left";


    /* --------------------------------------------------------
       SEMBUNYIKAN SEMUA HALAMAN
    -------------------------------------------------------- */

    PAGE_ORDER.forEach(
        function (id) {

            const page =
                document.getElementById(id);


            if (!page) {

                return;

            }


            page.classList.remove(
                "active",
                "slide-in-right",
                "slide-in-left"
            );

        }
    );


    /* --------------------------------------------------------
       TAMPILKAN HALAMAN TUJUAN
    -------------------------------------------------------- */

    const target =
        document.getElementById(pageId);


    if (!target) {

        return;

    }


    target.classList.add(
        "active"
    );


    if (useAnimation) {

        target.classList.add(
            direction
        );

    }


    currentPageIndex =
        targetIndex;


    /* --------------------------------------------------------
       STATUS MENU NAVIGASI
    -------------------------------------------------------- */

    navLinks.forEach(
        function (link) {

            link.classList.toggle(
                "active",
                link.dataset.page === pageId
            );

        }
    );


    /* --------------------------------------------------------
       STATUS PAGER
    -------------------------------------------------------- */

    updatePagerDots();


    refreshNavigationLocks();


    /* --------------------------------------------------------
       HASH URL
    -------------------------------------------------------- */

    if (PAGE_HASHES[pageId]) {

        history.replaceState(
            null,
            "",
            "#" + PAGE_HASHES[pageId]
        );

    }


    /* --------------------------------------------------------
       SCROLL KE ATAS
    -------------------------------------------------------- */

    target.scrollTop = 0;

    window.scrollTo(0, 0);

}


/* ============================================================
   TITIK PAGER
============================================================ */

function buildPagerDots() {

    if (!pagerDots) {

        return;

    }


    pagerDots.innerHTML = "";


    PAGE_ORDER.forEach(
        function (id, index) {

            const dot =
                document.createElement("button");


            dot.type = "button";

            dot.className = "pager-dot";

            dot.setAttribute(
                "aria-label",
                "Halaman " + (index + 1)
            );


            dot.addEventListener(
                "click",
                function () {

                    goToPage(id);

                }
            );


            pagerDots.appendChild(dot);

        }
    );

}


function updatePagerDots() {

    if (!pagerDots) {

        return;

    }


    const dots =
        pagerDots.children;


    for (let i = 0; i < dots.length; i++) {

        dots[i].classList.toggle(
            "active",
            i === currentPageIndex
        );

    }

}


/* ============================================================
   KUNCI NAVIGASI
   Tombol berikutnya, titik pager, dan menu dikunci
   jika halaman tujuan belum terisi
============================================================ */

function refreshNavigationLocks() {

    if (pagerPrev) {

        pagerPrev.disabled =
            currentPageIndex === 0;

    }


    if (pagerNext) {

        const nextId =
            PAGE_ORDER[currentPageIndex + 1];


        pagerNext.disabled =
            !nextId ||
            !canAccessPage(nextId);

    }


    if (pagerDots) {

        const dots =
            pagerDots.children;


        for (let i = 0; i < dots.length; i++) {

            const locked =
                !canAccessPage(PAGE_ORDER[i]);


            dots[i].classList.toggle(
                "locked",
                locked
            );

            dots[i].disabled = locked;

        }

    }


    navLinks.forEach(
        function (link) {

            link.classList.toggle(
                "locked",
                !canAccessPage(link.dataset.page)
            );

        }
    );

}


/* ============================================================
   PESAN PENGINGAT NAVIGASI
============================================================ */

let navHintTimer = null;


function showNavigationHint() {

    let hint =
        document.getElementById("navHint");


    if (!hint) {

        hint =
            document.createElement("div");

        hint.id = "navHint";

        hint.className = "nav-hint";

        document.body.appendChild(hint);

    }


    hint.textContent =
        "Unggah dan identifikasi gambar terlebih dahulu.";


    hint.classList.add("show");


    clearTimeout(navHintTimer);


    navHintTimer = setTimeout(
        function () {

            hint.classList.remove("show");

        },
        2600
    );

}


/* ============================================================
   EVENT NAVIGASI
============================================================ */

navLinks.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                goToPage(
                    this.dataset.page
                );

            }
        );

    }
);


document
    .querySelectorAll("[data-goto]")
    .forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    goToPage(
                        this.dataset.goto
                    );

                }
            );

        }
    );


if (pagerPrev) {

    pagerPrev.addEventListener(
        "click",
        function () {

            goToPage(
                PAGE_ORDER[currentPageIndex - 1]
            );

        }
    );

}


if (pagerNext) {

    pagerNext.addEventListener(
        "click",
        function () {

            goToPage(
                PAGE_ORDER[currentPageIndex + 1]
            );

        }
    );

}


/* ============================================================
   HALAMAN AWAL (BERDASARKAN HASH URL)
============================================================ */

buildPagerDots();


(function () {

    const hash =
        window.location.hash.replace("#", "");


    const initialPage =
        PAGE_ORDER.find(
            function (id) {

                return PAGE_HASHES[id] === hash;

            }
        );


    const startPage =
        initialPage && canAccessPage(initialPage)
            ? initialPage
            : "page-beranda";


    goToPage(
        startPage,
        false
    );

})();


/* ============================================================
   SELESAI
============================================================ */

console.log(
    "RIMPANG AI - JavaScript siap digunakan."
);