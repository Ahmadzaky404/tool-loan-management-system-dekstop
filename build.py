#!/usr/bin/env python3
"""
Script untuk build aplikasi menjadi executable (.exe)
Menggunakan PyInstaller
"""

import os
import sys
import shutil
from pathlib import Path


def check_pyinstaller():
    """Check apakah PyInstaller sudah terinstall"""
    try:
        import PyInstaller
        print("✓ PyInstaller tersedia")
        return True
    except ImportError:
        print("✗ PyInstaller tidak ditemukan")
        print("\nInstall dengan: pip install pyinstaller")
        return False


def clean_build():
    """Hapus folder build dan dist lama"""
    print("\n📁 Cleaning old build files...")
    
    folders = ['build', 'dist', '__pycache__']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"   Removed: {folder}/")
    
    # Hapus .spec files
    for spec in Path('.').glob('*.spec'):
        spec.unlink()
        print(f"   Removed: {spec}")


def build_exe():
    """Build executable"""
    print("\n🔨 Building executable...")
    print("   This may take a few minutes...\n")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--name=PeminjamanAlat',
        '--onefile',
        '--windowed',
        '--icon=assets/logo.ico' if os.path.exists('assets/logo.ico') else '',
        '--add-data=config.py:.',
        '--hidden-import=mysql.connector',
        '--hidden-import=bcrypt',
        '--hidden-import=PIL',
        '--hidden-import=customtkinter',
        '--collect-all=customtkinter',
        '--noconsole',
        'main.py'
    ]
    
    # Remove empty strings
    cmd = [c for c in cmd if c]
    
    # Run PyInstaller
    import subprocess
    result = subprocess.run(cmd, capture_output=False)
    
    return result.returncode == 0


def create_readme():
    """Buat README untuk distribusi"""
    readme = """
# Aplikasi Peminjaman Alat - Portable Version

## Cara Menggunakan

1. Pastikan MySQL Server sudah berjalan
2. Buat database: `peminjaman_alat`
3. Import schema SQL (lihat DATABASE_MYSQL.md)
4. Edit config.py sesuai koneksi MySQL Anda
5. Jalankan PeminjamanAlat.exe

## Akun Default

- Admin: admin@example.com / password
- Petugas: petugas@example.com / password
- Peminjam: peminjam@example.com / password

## Troubleshooting

Jika aplikasi tidak berjalan:
- Cek MySQL sudah berjalan
- Cek database sudah dibuat
- Cek konfigurasi di config.py
- Jalankan dari command prompt untuk melihat error

## Support

Untuk bantuan lebih lanjut, lihat dokumentasi lengkap di repository.
"""
    
    with open('dist/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print("✓ README.txt created")


def copy_files():
    """Copy file-file penting ke folder dist"""
    print("\n📋 Copying required files...")
    
    files_to_copy = [
        'config.py',
        'requirements.txt',
        'DATABASE_MYSQL.md',
        'DOKUMENTASI_APLIKASI.md',
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, 'dist/')
            print(f"   Copied: {file}")


def main():
    print("\n" + "=" * 60)
    print("  BUILD EXECUTABLE - Aplikasi Peminjaman Alat")
    print("=" * 60)
    
    # Check PyInstaller
    if not check_pyinstaller():
        return 1
    
    # Clean old builds
    clean_build()
    
    # Build
    if not build_exe():
        print("\n✗ Build failed!")
        return 1
    
    # Post-build
    create_readme()
    copy_files()
    
    print("\n" + "=" * 60)
    print("✓ Build berhasil!")
    print("=" * 60)
    print("\n📦 Executable tersedia di: dist/PeminjamanAlat.exe")
    print("\n📝 Catatan:")
    print("   • Copy folder 'dist' ke komputer target")
    print("   • Pastikan MySQL sudah terinstall di target")
    print("   • Edit config.py sesuai koneksi MySQL")
    print("   • Jalankan PeminjamanAlat.exe\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
