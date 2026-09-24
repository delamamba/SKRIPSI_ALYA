#!/bin/bash
# ============================================
# RIMPANG AI - Jalankan Website
# Cara pakai:  ./jalankan.sh
# ============================================

cd "$(dirname "$0")"

export CUDA_VISIBLE_DEVICES=1
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

../.venv/bin/python -c "import app; app.load_model(); app.app.run(host='127.0.0.1', port=5001, debug=False)"
