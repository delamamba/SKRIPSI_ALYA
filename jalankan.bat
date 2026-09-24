@echo off
REM ============================================
REM RIMPANG AI - Jalankan Website (Windows)
REM Cara pakai: klik dua kali file ini,
REM             lalu buka http://IP-KOMPUTER:5001 dari HP
REM ============================================

cd /d "%~dp0"

REM Buat ulang venv jika belum ada atau interpreter-nya sudah tidak valid
if not exist ".venv\Scripts\python.exe" goto setup_venv
.venv\Scripts\python.exe -c "import sys" >nul 2>&1
if errorlevel 1 (
    echo Virtual environment lama tidak valid, membuat ulang...
    rmdir /s /q .venv
    goto setup_venv
)
goto start_server

:setup_venv
echo Membuat virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Gagal membuat virtual environment. Pastikan Python sudah terpasang.
    pause
    exit /b 1
)
echo Menginstall library - ini hanya sekali dan butuh beberapa menit...
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Gagal menginstall kebutuhan aplikasi.
    pause
    exit /b 1
)

:start_server
echo Menjalankan RIMPANG AI...
.venv\Scripts\python -c "import app; app.load_model(); app.app.run(host='0.0.0.0', port=5001, debug=False)"

pause
