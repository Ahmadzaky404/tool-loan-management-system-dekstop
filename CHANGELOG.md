# Changelog

Semua perubahan penting pada project ini akan didokumentasikan di file ini.

## [1.1.0] - 2026-02-26

### Added
- Fitur Laporan dengan 3 tab (Peminjaman, Pengembalian, Denda)
- Export laporan ke Excel dengan format profesional
- Filter laporan berdasarkan tanggal dan status
- Auto-load data laporan saat halaman dibuka
- Input denda manual untuk barang rusak dan hilang saat verifikasi
- Placeholder tarif default pada input denda manual
- Light/Dark theme toggle dengan auto-restart
- Persistensi preferensi theme menggunakan JSON
- Auto-install dependencies saat menjalankan run.bat/run.sh
- Library openpyxl untuk export Excel
- Library reportlab untuk export PDF (placeholder)

### Changed
- Tampilan filter laporan menggunakan card layout yang lebih rapi
- Tombol filter dan export dipisah untuk UX yang lebih baik
- Label filter ditampilkan di atas input field
- Verifikasi pengembalian sekarang support input denda custom
- Script run.bat/run.sh sekarang selalu update dependencies
- Warna light theme disesuaikan dengan standar modern UI

### Fixed
- Error "datetime.date and NoneType" saat verifikasi pengembalian
- Query laporan yang error karena kolom 'phone' tidak ada
- Data tanggal_kembali NULL pada tabel peminjaman
- Tombol submit tidak terlihat pada dialog ajukan pengembalian
- Height modal yang terlalu tinggi

### Technical
- Menambahkan db/laporan_db.py untuk query laporan
- Menambahkan views/laporan_view.py untuk UI laporan
- Menambahkan theme_config.json untuk menyimpan preferensi theme
- Update config.py dengan sistem theme yang lebih baik
- Menambahkan fix_tanggal_kembali.py untuk maintenance database
- Update requirements.txt dengan openpyxl dan reportlab

## [1.0.0] - 2026-02-25

### Added

#### Autentikasi & Session
- Login dengan email & password (bcrypt)
- Session management
- Role-based access control (Admin, Petugas, Peminjam)
- Logout functionality

#### Dashboard
- Dashboard berbeda per role
- Statistik real-time:
  - Admin: Total alat, peminjaman, denda, user
  - Petugas: Peminjaman pending, hari ini
  - Peminjam: Peminjaman aktif, pending, denda

#### Manajemen Alat (Admin)
- CRUD alat lengkap
- CRUD kategori alat
- Filter & search alat
- Status alat (tersedia, dipinjam, rusak)
- Tracking stok real-time

#### Peminjaman
- Pengajuan peminjaman (Peminjam)
- Approval/rejection (Admin/Petugas)
- Tracking status peminjaman
- Detail peminjaman dengan daftar alat
- Validasi stok otomatis
- Notifikasi otomatis

#### Pengembalian
- Form pengembalian dengan kondisi alat
- Verifikasi pengembalian (Admin/Petugas)
- Kalkulasi denda otomatis:
  - Keterlambatan: Rp 10.000/hari
  - Rusak: Rp 50.000/unit
  - Hilang: Rp 500.000/unit
- Update stok & status alat otomatis

#### Denda
- Daftar denda per user
- Form pembayaran denda
- Status pembayaran (Belum Bayar/Lunas)
- Metode pembayaran (Tunai/Transfer)
- History pembayaran

#### Notifikasi
- Notifikasi real-time
- Badge counter unread
- Polling setiap 30 detik
- Tandai dibaca/belum dibaca
- Notifikasi untuk:
  - Peminjaman baru
  - Approval/rejection
  - Verifikasi pengembalian
  - Denda baru

#### Manajemen User (Admin)
- CRUD user lengkap
- Toggle aktif/nonaktif user
- Filter by role
- Password hashing otomatis

#### Log Aktivitas (Admin)
- Tracking semua aktivitas user
- Filter by user
- Detail IP address & user agent
- Timestamp lengkap

#### UI/UX
- Modern dark theme
- Responsive layout
- Sidebar navigation
- Custom widgets:
  - StatCard untuk statistik
  - DataTable untuk tabel data
  - SectionHeader untuk judul section
- Color-coded status badges
- Loading states
- Error handling

#### Database
- MySQL connection pooling
- Transaction support
- Prepared statements (SQL injection prevention)
- Soft delete untuk peminjaman
- Foreign key constraints

### Technical Stack
- Python 3.10+
- CustomTkinter 5.2+
- MySQL Connector Python 8.3+
- Bcrypt 4.1+
- Pillow 10.0+
- tkcalendar 1.6+

### Documentation
- README.md lengkap
- DOKUMENTASI_APLIKASI.md
- DATABASE_MYSQL.md
- DESKTOP_PYTHON_TKINTER.md
- Inline code comments

### Development Tools
- run.bat untuk Windows
- run.sh untuk Linux/Mac
- .gitignore
- requirements.txt
- Virtual environment support

---

Format: [version] - YYYY-MM-DD

Tipe perubahan:
- Added: Fitur baru
- Changed: Perubahan pada fitur yang ada
- Deprecated: Fitur yang akan dihapus
- Removed: Fitur yang dihapus
- Fixed: Bug fix
- Security: Security fix
- Technical: Perubahan teknis/internal
