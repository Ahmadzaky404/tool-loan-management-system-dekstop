# Aplikasi Peminjaman Alat - Desktop

Aplikasi desktop untuk manajemen peminjaman peralatan menggunakan Python + CustomTkinter + MySQL.

> **Catatan:** Project ini dibuat sebagai penyelesaian tugas sekolah untuk mata pelajaran Rekayasa Perangkat Lunak basis Desktop.

## Fitur Utama

- Login & Autentikasi (Admin, Petugas, Peminjam)
- Dashboard dengan statistik real-time
- Manajemen Alat & Kategori
- Peminjaman & Pengembalian
- Kalkulasi Denda Otomatis
- Laporan dengan Export Excel
- Notifikasi Real-time
- Light/Dark Theme

## Teknologi yang Digunakan

### Backend
- **Python 3.10+** - Bahasa pemrograman utama
- **MySQL 8.0+** - Database relational untuk menyimpan data
- **mysql-connector-python** - Driver untuk koneksi Python ke MySQL
- **Bcrypt** - Library untuk hashing password (keamanan)

### Frontend/UI
- **CustomTkinter 5.2+** - Framework UI modern berbasis Tkinter
- **Pillow** - Library untuk image processing dan manipulasi gambar
- **tkcalendar** - Widget kalender untuk input tanggal

### Fitur Tambahan
- **OpenPyXL** - Library untuk membuat dan membaca file Excel (.xlsx)
- **ReportLab** - Library untuk generate PDF (laporan)

### Arsitektur
- **MVC Pattern** - Pemisahan Model (db/), View (views/), Controller (utils/)
- **Database Connection Pooling** - Manajemen koneksi database yang efisien
- **Session Management** - Pengelolaan sesi login user
- **Role-Based Access Control (RBAC)** - Kontrol akses berdasarkan role

## Instalasi

### Cara Cepat (Recommended)

**Windows:**
1. Pastikan Python 3.10+ dan MySQL sudah terinstall
2. Setup database (lihat bagian Setup Database di bawah)
3. **Double-click file `run.bat`**
4. Selesai! Aplikasi akan otomatis:
   - Membuat virtual environment
   - Install semua dependencies
   - Menjalankan aplikasi

**Linux/Mac:**
1. Pastikan Python 3.10+ dan MySQL sudah terinstall
2. Setup database (lihat bagian Setup Database di bawah)
3. Jalankan: `chmod +x run.sh && ./run.sh`
4. Selesai!

### Setup Database

1. Buat database:
```bash
mysql -u root -p
```

```sql
CREATE DATABASE peminjaman_alat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

2. Import schema:
```bash
mysql -u root -p peminjaman_alat < schema.sql
mysql -u root -p peminjaman_alat < fix_tanggal_kembali.sql
```

3. Setup data sample (opsional):
```bash
python setup_sample_data.py
```

4. Edit `config.py` dan sesuaikan password MySQL:


### Instalasi Manual (Jika Tidak Pakai run.bat)

Jika Anda ingin install manual tanpa run.bat:

1. Buat virtual environment:
```bash
python -m venv venv
```

2. Aktifkan virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

Atau install satu per satu:
```bash
pip install customtkinter>=5.2.0
pip install mysql-connector-python>=8.3.0
pip install bcrypt>=4.1.0
pip install Pillow>=10.0.0
pip install tkcalendar>=1.6.1
pip install openpyxl>=3.1.0
pip install reportlab>=4.0.0
```

Penjelasan dependencies:
- **customtkinter** - Framework UI modern untuk desktop
- **mysql-connector-python** - Koneksi ke database MySQL
- **bcrypt** - Hashing password untuk keamanan
- **Pillow** - Image processing untuk UI
- **tkcalendar** - Widget kalender untuk input tanggal
- **openpyxl** - Export laporan ke Excel
- **reportlab** - Export laporan ke PDF

4. Jalankan aplikasi:
```bash
python main.py
```

## Akun Default

Setelah setup data sample, login dengan:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@example.com | password |
| Petugas | petugas@example.com | password |
| Peminjam | peminjam@example.com | password |

## Troubleshooting

**Error: "Tidak dapat terhubung ke database"**
- Pastikan MySQL sudah berjalan
- Cek password di `config.py`

**Error: "ModuleNotFoundError"**
- Jalankan ulang `run.bat` atau `pip install -r requirements.txt`

**Error: "datetime.date and NoneType"**
- Jalankan: `python fix_tanggal_kembali.py`

## Dokumentasi Lengkap

Untuk dokumentasi lengkap, lihat:
- [QUICKSTART.md](QUICKSTART.md) - Panduan cepat
- [DOKUMENTASI_APLIKASI.md](DOKUMENTASI_APLIKASI.md) - Dokumentasi sistem lengkap
- [FAQ.md](FAQ.md) - Pertanyaan yang sering diajukan

---

## Author

**Nama:** Romeo Aditya  
**Kelas:** XI-RPL  
**Project:** Tool Loan Management System  
**Tahun:** 2026

---

**Versi:** 1.1.0 | **Lisensi:** MIT
