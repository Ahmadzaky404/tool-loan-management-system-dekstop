@echo off
echo ========================================
echo   Aplikasi Peminjaman Alat - Desktop
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python tidak ditemukan!
    echo Silakan install Python 3.10+ terlebih dahulu.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python ditemukan
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [INFO] Virtual environment belum ada, membuat...
    python -m venv venv
    echo [OK] Virtual environment berhasil dibuat
    echo.
)

REM Activate virtual environment
echo [INFO] Mengaktifkan virtual environment...
call venv\Scripts\activate.bat

REM Always check and install/update dependencies
echo [INFO] Memeriksa dan menginstall dependencies...
echo.
pip install -r requirements.txt --upgrade
echo.
echo [OK] Dependencies berhasil diinstall/diupdate
echo.

REM Run the application
echo [INFO] Menjalankan aplikasi...
echo.
python main.py

REM Deactivate virtual environment
deactivate

pause
