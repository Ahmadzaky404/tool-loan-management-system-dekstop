#!/bin/bash

echo "========================================"
echo "  Aplikasi Peminjaman Alat - Desktop"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 tidak ditemukan!"
    echo "Silakan install Python 3.10+ terlebih dahulu."
    exit 1
fi

echo "[INFO] Python ditemukan: $(python3 --version)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "[INFO] Virtual environment belum ada, membuat..."
    python3 -m venv venv
    echo "[OK] Virtual environment berhasil dibuat"
    echo ""
fi

# Activate virtual environment
echo "[INFO] Mengaktifkan virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "[INFO] Memeriksa dan menginstall dependencies..."
echo ""
pip install -r requirements.txt --upgrade
echo ""
echo "[OK] Dependencies berhasil diinstall/diupdate"
echo ""

# Run the application
echo "[INFO] Menjalankan aplikasi..."
echo ""
python3 main.py

# Deactivate virtual environment
deactivate
