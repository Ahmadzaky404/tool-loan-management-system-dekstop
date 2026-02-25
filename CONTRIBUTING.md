# Contributing to Aplikasi Peminjaman Alat

Terima kasih atas minat Anda untuk berkontribusi!

## Cara Berkontribusi

### 1. Fork & Clone

```bash
# Fork repository di GitHub
# Kemudian clone fork Anda
git clone https://github.com/YOUR_USERNAME/peminjaman-alat-desktop.git
cd peminjaman-alat-desktop
```

### 2. Setup Development Environment

```bash
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Buat Branch Baru

```bash
git checkout -b feature/nama-fitur-anda
# atau
git checkout -b fix/nama-bug-yang-diperbaiki
```

### 4. Coding Standards

#### Python Style Guide
- Ikuti [PEP 8](https://pep8.org/)
- Gunakan 4 spasi untuk indentasi
- Maximum line length: 100 karakter
- Gunakan docstrings untuk fungsi/class

#### Naming Conventions
```python
# Variables & functions: snake_case
user_name = "John"
def get_user_data():
    pass

# Classes: PascalCase
class UserManager:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY = 3
DB_CONFIG = {}

# Private methods: _leading_underscore
def _internal_method():
    pass
```

#### Code Organization
```python
# Import order:
# 1. Standard library
import os
from datetime import datetime

# 2. Third-party
import customtkinter as ctk
from mysql.connector import Error

# 3. Local
from config import DB_CONFIG
from utils.auth import login
```

### 5. Database Changes

Jika Anda menambah/mengubah struktur database:

1. Update file `DATABASE_MYSQL.md`
2. Buat migration script jika perlu
3. Update dokumentasi di `DOKUMENTASI_APLIKASI.md`

### 6. Testing

Sebelum submit PR, pastikan:

```bash
# Test koneksi database
python -c "from db.connection import Database; Database.get_connection(); print('OK')"

# Test login
python -c "from utils.auth import login; print(login('admin@example.com', 'password'))"

# Run aplikasi
python main.py
```

Test manual:
- Login berhasil dengan semua role
- Navigasi antar halaman lancar
- CRUD operations berfungsi
- Notifikasi muncul
- Error handling bekerja

### 7. Commit Messages

Gunakan format commit message yang jelas:

```
<type>: <subject>

<body (optional)>

<footer (optional)>
```

Types:
- `feat`: Fitur baru
- `fix`: Bug fix
- `docs`: Perubahan dokumentasi
- `style`: Format code (tidak mengubah logic)
- `refactor`: Refactoring code
- `test`: Menambah/update test
- `chore`: Maintenance tasks

Contoh:
```
feat: tambah fitur export laporan ke Excel

- Tambah button export di laporan view
- Implementasi export menggunakan openpyxl
- Update requirements.txt

Closes #123
```

### 8. Pull Request

1. Push branch Anda:
```bash
git push origin feature/nama-fitur-anda
```

2. Buat Pull Request di GitHub dengan:
   - Judul yang jelas
   - Deskripsi lengkap perubahan
   - Screenshot jika ada perubahan UI
   - Link ke issue terkait (jika ada)

3. Tunggu review dan feedback

## Melaporkan Bug

Gunakan GitHub Issues dengan template:

```markdown
**Deskripsi Bug**
Penjelasan singkat tentang bug

**Cara Reproduksi**
1. Buka halaman X
2. Klik button Y
3. Error muncul

**Expected Behavior**
Yang seharusnya terjadi

**Screenshots**
Jika ada

**Environment**
- OS: Windows 10
- Python: 3.11
- MySQL: 8.0
```

## Mengusulkan Fitur

Gunakan GitHub Issues dengan label `enhancement`:

```markdown
**Fitur yang Diusulkan**
Deskripsi fitur

**Motivasi**
Kenapa fitur ini penting

**Alternatif**
Solusi alternatif yang sudah dipertimbangkan

**Mockup/Wireframe**
Jika ada
```

## Update Dokumentasi

Jika Anda menambah fitur baru, update:

1. `README.md` - Jika ada perubahan instalasi/usage
2. `DOKUMENTASI_APLIKASI.md` - Dokumentasi lengkap fitur
3. `CHANGELOG.md` - Catat perubahan
4. Inline comments di code

## UI/UX Guidelines

### Colors
Gunakan konstanta dari `config.py`:
```python
from config import PRIMARY, SUCCESS, DANGER, WARNING
```

### Spacing
- Padding: 8, 12, 16, 20, 24, 32
- Margin: sama dengan padding
- Border radius: 8, 10, 12, 16

### Typography
```python
# Heading
font=ctk.CTkFont(size=22, weight="bold")

# Subheading
font=ctk.CTkFont(size=16, weight="bold")

# Body
font=ctk.CTkFont(size=13)

# Small
font=ctk.CTkFont(size=11)
```

### Components
Gunakan komponen yang sudah ada di `components/widgets.py`:
- `StatCard` untuk statistik
- `DataTable` untuk tabel
- `SectionHeader` untuk judul section
- `Modal` untuk dialog
- `DatePicker` untuk input tanggal

## Security

- JANGAN commit credentials atau API keys
- JANGAN commit file `config.py` dengan password real
- Gunakan environment variables untuk sensitive data
- Selalu validasi input user
- Gunakan prepared statements untuk query SQL

## Pertanyaan?

Jika ada pertanyaan:
1. Cek dokumentasi terlebih dahulu
2. Search di GitHub Issues
3. Buat issue baru dengan label `question`

## Code of Conduct

- Bersikap profesional dan menghormati
- Konstruktif dalam feedback
- Fokus pada kode, bukan personal
- Bantu sesama contributor

## Terima Kasih!

Kontribusi Anda sangat berarti untuk project ini. Happy coding!
