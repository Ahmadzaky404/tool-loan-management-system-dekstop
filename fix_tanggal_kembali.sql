-- ============================================
-- Script untuk memperbaiki data tanggal_kembali yang NULL
-- Jalankan script ini jika ada error terkait tanggal_kembali NULL
-- ============================================

USE `peminjaman_alat`;

-- Cek data peminjaman yang tanggal_kembali nya NULL
SELECT 
    id, 
    user_id, 
    tanggal_pinjam, 
    tanggal_kembali, 
    status,
    'Data dengan tanggal_kembali NULL' AS keterangan
FROM peminjaman
WHERE tanggal_kembali IS NULL;

-- Update tanggal_kembali yang NULL dengan tanggal_pinjam + 7 hari (default)
UPDATE peminjaman
SET tanggal_kembali = DATE_ADD(tanggal_pinjam, INTERVAL 7 DAY),
    updated_at = NOW()
WHERE tanggal_kembali IS NULL;

-- Verifikasi hasil - seharusnya tidak ada data yang NULL lagi
SELECT 
    id, 
    user_id, 
    tanggal_pinjam, 
    tanggal_kembali, 
    status,
    'Verifikasi setelah update' AS keterangan
FROM peminjaman
WHERE tanggal_kembali IS NULL;

-- Jika masih ada yang NULL, set ke tanggal hari ini
UPDATE peminjaman
SET tanggal_kembali = CURDATE(),
    updated_at = NOW()
WHERE tanggal_kembali IS NULL;

-- Final check
SELECT 
    COUNT(*) AS total_peminjaman,
    SUM(CASE WHEN tanggal_kembali IS NULL THEN 1 ELSE 0 END) AS tanggal_null,
    SUM(CASE WHEN tanggal_kembali IS NOT NULL THEN 1 ELSE 0 END) AS tanggal_valid
FROM peminjaman;
