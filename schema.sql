-- ============================================
-- DATABASE SCHEMA - APLIKASI PEMINJAMAN ALAT
-- ============================================
-- Database: peminjaman_alat
-- Charset: utf8mb4
-- Collation: utf8mb4_unicode_ci
-- Created: 2026-02-25
-- ============================================

-- Buat database
CREATE DATABASE IF NOT EXISTS `peminjaman_alat`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `peminjaman_alat`;

-- ============================================
-- TABEL: roles
-- Deskripsi: Menyimpan role/peran user
-- ============================================
CREATE TABLE IF NOT EXISTS `roles` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL COMMENT 'Nama role: admin, petugas, peminjam',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roles_name_unique` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel role/peran pengguna';

-- ============================================
-- TABEL: users
-- Deskripsi: Menyimpan data pengguna
-- ============================================
CREATE TABLE IF NOT EXISTS `users` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL COMMENT 'Nama lengkap user',
  `email` VARCHAR(255) NOT NULL COMMENT 'Email untuk login',
  `email_verified_at` TIMESTAMP NULL DEFAULT NULL,
  `password` VARCHAR(255) NOT NULL COMMENT 'Password hash (bcrypt)',
  `role_id` BIGINT UNSIGNED NOT NULL DEFAULT 3 COMMENT 'FK ke roles',
  `is_active` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1=aktif, 0=nonaktif',
  `remember_token` VARCHAR(100) NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_email_unique` (`email`),
  KEY `users_role_id_index` (`role_id`),
  KEY `users_is_active_index` (`is_active`),
  CONSTRAINT `users_role_id_foreign`
    FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel pengguna sistem';

-- ============================================
-- TABEL: kategori
-- Deskripsi: Kategori alat
-- ============================================
CREATE TABLE IF NOT EXISTS `kategori` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nama` VARCHAR(100) NOT NULL COMMENT 'Nama kategori',
  `deskripsi` TEXT NULL DEFAULT NULL COMMENT 'Deskripsi kategori',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `kategori_nama_unique` (`nama`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel kategori alat';

-- ============================================
-- TABEL: alat
-- Deskripsi: Master data alat/peralatan
-- ============================================
CREATE TABLE IF NOT EXISTS `alat` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `kategori_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke kategori',
  `nama` VARCHAR(255) NOT NULL COMMENT 'Nama alat',
  `kode` VARCHAR(50) NOT NULL COMMENT 'Kode unik alat',
  `deskripsi` TEXT NULL DEFAULT NULL COMMENT 'Deskripsi alat',
  `gambar` VARCHAR(255) NULL DEFAULT NULL COMMENT 'Path file gambar',
  `stok` INT NOT NULL DEFAULT 0 COMMENT 'Jumlah stok tersedia',
  `status` ENUM('tersedia','dipinjam','rusak') NOT NULL DEFAULT 'tersedia' COMMENT 'Status alat',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `alat_kode_unique` (`kode`),
  KEY `alat_kategori_id_index` (`kategori_id`),
  KEY `alat_status_index` (`status`),
  KEY `alat_kode_index` (`kode`),
  KEY `alat_nama_index` (`nama`),
  CONSTRAINT `alat_kategori_id_foreign`
    FOREIGN KEY (`kategori_id`) REFERENCES `kategori` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel master alat/peralatan';

-- ============================================
-- TABEL: peminjaman
-- Deskripsi: Header peminjaman alat
-- ============================================
CREATE TABLE IF NOT EXISTS `peminjaman` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke users (peminjam)',
  `tanggal_pinjam` DATE NOT NULL COMMENT 'Tanggal mulai pinjam',
  `tanggal_kembali` DATE NOT NULL COMMENT 'Tanggal rencana kembali',
  `status` ENUM('pending','disetujui','ditolak','selesai') NOT NULL DEFAULT 'pending' COMMENT 'Status peminjaman',
  `alasan_penolakan` TEXT NULL DEFAULT NULL COMMENT 'Alasan jika ditolak',
  `approved_by` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'FK ke users (yang approve)',
  `deleted_at` TIMESTAMP NULL DEFAULT NULL COMMENT 'Soft delete',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `peminjaman_user_id_index` (`user_id`),
  KEY `peminjaman_status_index` (`status`),
  KEY `peminjaman_tanggal_pinjam_index` (`tanggal_pinjam`),
  KEY `peminjaman_tanggal_kembali_index` (`tanggal_kembali`),
  KEY `peminjaman_approved_by_index` (`approved_by`),
  KEY `peminjaman_deleted_at_index` (`deleted_at`),
  CONSTRAINT `peminjaman_user_id_foreign`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `peminjaman_approved_by_foreign`
    FOREIGN KEY (`approved_by`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel header peminjaman';

-- ============================================
-- TABEL: detail_peminjaman
-- Deskripsi: Detail alat yang dipinjam
-- ============================================
CREATE TABLE IF NOT EXISTS `detail_peminjaman` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `peminjaman_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke peminjaman',
  `alat_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke alat',
  `jumlah` INT NOT NULL DEFAULT 1 COMMENT 'Jumlah alat yang dipinjam',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `detail_peminjaman_peminjaman_id_index` (`peminjaman_id`),
  KEY `detail_peminjaman_alat_id_index` (`alat_id`),
  CONSTRAINT `detail_peminjaman_peminjaman_id_foreign`
    FOREIGN KEY (`peminjaman_id`) REFERENCES `peminjaman` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detail_peminjaman_alat_id_foreign`
    FOREIGN KEY (`alat_id`) REFERENCES `alat` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel detail alat yang dipinjam';

-- ============================================
-- TABEL: pengembalian
-- Deskripsi: Header pengembalian alat
-- ============================================
CREATE TABLE IF NOT EXISTS `pengembalian` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `peminjaman_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke peminjaman',
  `tanggal_kembali_aktual` DATE NOT NULL COMMENT 'Tanggal aktual dikembalikan',
  `kondisi_alat` ENUM('baik','rusak','hilang','mixed') NOT NULL DEFAULT 'baik' COMMENT 'Kondisi alat saat dikembalikan',
  `catatan` TEXT NULL DEFAULT NULL COMMENT 'Catatan pengembalian',
  `verified_by` BIGINT UNSIGNED NULL DEFAULT NULL COMMENT 'FK ke users (yang verifikasi)',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `pengembalian_peminjaman_id_index` (`peminjaman_id`),
  KEY `pengembalian_verified_by_index` (`verified_by`),
  KEY `pengembalian_tanggal_kembali_aktual_index` (`tanggal_kembali_aktual`),
  CONSTRAINT `pengembalian_peminjaman_id_foreign`
    FOREIGN KEY (`peminjaman_id`) REFERENCES `peminjaman` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pengembalian_verified_by_foreign`
    FOREIGN KEY (`verified_by`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel header pengembalian';

-- ============================================
-- TABEL: detail_pengembalian
-- Deskripsi: Detail kondisi alat yang dikembalikan
-- ============================================
CREATE TABLE IF NOT EXISTS `detail_pengembalian` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `pengembalian_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke pengembalian',
  `alat_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke alat',
  `jumlah_baik` INT NOT NULL DEFAULT 0 COMMENT 'Jumlah alat kondisi baik',
  `jumlah_rusak` INT NOT NULL DEFAULT 0 COMMENT 'Jumlah alat kondisi rusak',
  `jumlah_hilang` INT NOT NULL DEFAULT 0 COMMENT 'Jumlah alat hilang',
  `denda_rusak` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Nominal denda kerusakan',
  `denda_hilang` DECIMAL(10,2) NOT NULL DEFAULT 0.00 COMMENT 'Nominal denda kehilangan',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `detail_pengembalian_pengembalian_id_index` (`pengembalian_id`),
  KEY `detail_pengembalian_alat_id_index` (`alat_id`),
  CONSTRAINT `detail_pengembalian_pengembalian_id_foreign`
    FOREIGN KEY (`pengembalian_id`) REFERENCES `pengembalian` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `detail_pengembalian_alat_id_foreign`
    FOREIGN KEY (`alat_id`) REFERENCES `alat` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel detail kondisi alat yang dikembalikan';

-- ============================================
-- TABEL: denda
-- Deskripsi: Denda peminjaman
-- ============================================
CREATE TABLE IF NOT EXISTS `denda` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `pengembalian_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke pengembalian',
  `jumlah` DECIMAL(10,2) NOT NULL COMMENT 'Total nominal denda',
  `keterangan` TEXT NULL DEFAULT NULL COMMENT 'Rincian denda',
  `status` ENUM('belum_bayar','lunas') NOT NULL DEFAULT 'belum_bayar' COMMENT 'Status pembayaran',
  `metode_pembayaran` ENUM('tunai','transfer') NULL DEFAULT NULL COMMENT 'Metode pembayaran',
  `bukti_pembayaran` VARCHAR(500) NULL DEFAULT NULL COMMENT 'Keterangan bukti bayar',
  `tanggal_bayar` DATETIME NULL DEFAULT NULL COMMENT 'Waktu pembayaran',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `denda_pengembalian_id_index` (`pengembalian_id`),
  KEY `denda_status_index` (`status`),
  KEY `denda_tanggal_bayar_index` (`tanggal_bayar`),
  CONSTRAINT `denda_pengembalian_id_foreign`
    FOREIGN KEY (`pengembalian_id`) REFERENCES `pengembalian` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel denda peminjaman';

-- ============================================
-- TABEL: log_aktivitas
-- Deskripsi: Log semua aktivitas user
-- ============================================
CREATE TABLE IF NOT EXISTS `log_aktivitas` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke users',
  `aktivitas` VARCHAR(255) NOT NULL COMMENT 'Nama aktivitas',
  `deskripsi` TEXT NULL DEFAULT NULL COMMENT 'Detail aktivitas',
  `ip_address` VARCHAR(45) NULL DEFAULT NULL COMMENT 'IP address user',
  `user_agent` TEXT NULL DEFAULT NULL COMMENT 'Browser/device info',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `log_aktivitas_user_id_index` (`user_id`),
  KEY `log_aktivitas_created_at_index` (`created_at`),
  CONSTRAINT `log_aktivitas_user_id_foreign`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel log aktivitas user';

-- ============================================
-- TABEL: notifications
-- Deskripsi: Notifikasi untuk user
-- ============================================
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT 'FK ke users (penerima)',
  `title` VARCHAR(255) NOT NULL COMMENT 'Judul notifikasi',
  `message` TEXT NOT NULL COMMENT 'Isi pesan',
  `type` VARCHAR(100) NOT NULL DEFAULT 'info' COMMENT 'Tipe notifikasi',
  `data` JSON NULL DEFAULT NULL COMMENT 'Data tambahan (JSON)',
  `is_read` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=belum dibaca, 1=sudah',
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `notifications_user_id_index` (`user_id`),
  KEY `notifications_is_read_index` (`is_read`),
  KEY `notifications_created_at_index` (`created_at`),
  CONSTRAINT `notifications_user_id_foreign`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel notifikasi user';

-- ============================================
-- TABEL: personal_access_tokens
-- Deskripsi: Token untuk API authentication (Laravel Sanctum)
-- ============================================
CREATE TABLE IF NOT EXISTS `personal_access_tokens` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `tokenable_type` VARCHAR(255) NOT NULL,
  `tokenable_id` BIGINT UNSIGNED NOT NULL,
  `name` VARCHAR(255) NOT NULL COMMENT 'Nama token',
  `token` VARCHAR(64) NOT NULL COMMENT 'Token hash',
  `abilities` TEXT NULL DEFAULT NULL COMMENT 'Permissions',
  `last_used_at` TIMESTAMP NULL DEFAULT NULL,
  `expires_at` TIMESTAMP NULL DEFAULT NULL,
  `created_at` TIMESTAMP NULL DEFAULT NULL,
  `updated_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `personal_access_tokens_token_unique` (`token`),
  KEY `personal_access_tokens_tokenable_type_tokenable_id_index` (`tokenable_type`, `tokenable_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel token API (Laravel Sanctum)';

-- ============================================
-- TABEL: sessions
-- Deskripsi: Session Laravel (jika menggunakan database driver)
-- ============================================
CREATE TABLE IF NOT EXISTS `sessions` (
  `id` VARCHAR(255) NOT NULL,
  `user_id` BIGINT UNSIGNED NULL DEFAULT NULL,
  `ip_address` VARCHAR(45) NULL DEFAULT NULL,
  `user_agent` TEXT NULL DEFAULT NULL,
  `payload` LONGTEXT NOT NULL,
  `last_activity` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `sessions_user_id_index` (`user_id`),
  KEY `sessions_last_activity_index` (`last_activity`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel session Laravel';

-- ============================================
-- TABEL: cache
-- Deskripsi: Cache Laravel (jika menggunakan database driver)
-- ============================================
CREATE TABLE IF NOT EXISTS `cache` (
  `key` VARCHAR(255) NOT NULL,
  `value` MEDIUMTEXT NOT NULL,
  `expiration` INT NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel cache Laravel';

CREATE TABLE IF NOT EXISTS `cache_locks` (
  `key` VARCHAR(255) NOT NULL,
  `owner` VARCHAR(255) NOT NULL,
  `expiration` INT NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel cache locks Laravel';

-- ============================================
-- TABEL: jobs
-- Deskripsi: Queue jobs Laravel (jika menggunakan database driver)
-- ============================================
CREATE TABLE IF NOT EXISTS `jobs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `queue` VARCHAR(255) NOT NULL,
  `payload` LONGTEXT NOT NULL,
  `attempts` TINYINT UNSIGNED NOT NULL,
  `reserved_at` INT UNSIGNED NULL DEFAULT NULL,
  `available_at` INT UNSIGNED NOT NULL,
  `created_at` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id`),
  KEY `jobs_queue_index` (`queue`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel queue jobs Laravel';

CREATE TABLE IF NOT EXISTS `job_batches` (
  `id` VARCHAR(255) NOT NULL,
  `name` VARCHAR(255) NOT NULL,
  `total_jobs` INT NOT NULL,
  `pending_jobs` INT NOT NULL,
  `failed_jobs` INT NOT NULL,
  `failed_job_ids` LONGTEXT NOT NULL,
  `options` MEDIUMTEXT NULL DEFAULT NULL,
  `cancelled_at` INT NULL DEFAULT NULL,
  `created_at` INT NOT NULL,
  `finished_at` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel job batches Laravel';

CREATE TABLE IF NOT EXISTS `failed_jobs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `uuid` VARCHAR(255) NOT NULL,
  `connection` TEXT NOT NULL,
  `queue` TEXT NOT NULL,
  `payload` LONGTEXT NOT NULL,
  `exception` LONGTEXT NOT NULL,
  `failed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `failed_jobs_uuid_unique` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabel failed jobs Laravel';

-- ============================================
-- INSERT DATA AWAL
-- ============================================

-- Insert roles
INSERT INTO `roles` (`id`, `name`, `created_at`, `updated_at`) VALUES
  (1, 'admin', NOW(), NOW()),
  (2, 'petugas', NOW(), NOW()),
  (3, 'peminjam', NOW(), NOW())
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`);

-- ============================================
-- VIEWS (Optional - untuk kemudahan query)
-- ============================================

-- View: Peminjaman dengan detail lengkap
CREATE OR REPLACE VIEW `v_peminjaman_lengkap` AS
SELECT 
  p.id,
  p.user_id,
  u.name AS nama_peminjam,
  u.email AS email_peminjam,
  p.tanggal_pinjam,
  p.tanggal_kembali,
  p.status,
  p.alasan_penolakan,
  p.approved_by,
  approver.name AS nama_approver,
  GROUP_CONCAT(CONCAT(a.nama, ' (', dp.jumlah, ')') SEPARATOR ', ') AS daftar_alat,
  p.created_at,
  p.updated_at
FROM peminjaman p
JOIN users u ON u.id = p.user_id
LEFT JOIN users approver ON approver.id = p.approved_by
LEFT JOIN detail_peminjaman dp ON dp.peminjaman_id = p.id
LEFT JOIN alat a ON a.id = dp.alat_id
WHERE p.deleted_at IS NULL
GROUP BY p.id;

-- View: Denda dengan detail lengkap
CREATE OR REPLACE VIEW `v_denda_lengkap` AS
SELECT 
  d.id,
  d.pengembalian_id,
  pen.peminjaman_id,
  p.user_id,
  u.name AS nama_peminjam,
  u.email AS email_peminjam,
  d.jumlah,
  d.keterangan,
  d.status,
  d.metode_pembayaran,
  d.bukti_pembayaran,
  d.tanggal_bayar,
  pen.tanggal_kembali_aktual,
  p.tanggal_kembali AS tanggal_kembali_rencana,
  DATEDIFF(pen.tanggal_kembali_aktual, p.tanggal_kembali) AS hari_terlambat,
  d.created_at,
  d.updated_at
FROM denda d
JOIN pengembalian pen ON pen.id = d.pengembalian_id
JOIN peminjaman p ON p.id = pen.peminjaman_id
JOIN users u ON u.id = p.user_id;

-- View: Statistik alat
CREATE OR REPLACE VIEW `v_statistik_alat` AS
SELECT 
  k.id AS kategori_id,
  k.nama AS kategori_nama,
  COUNT(a.id) AS total_alat,
  SUM(a.stok) AS total_stok,
  SUM(CASE WHEN a.status = 'tersedia' THEN 1 ELSE 0 END) AS alat_tersedia,
  SUM(CASE WHEN a.status = 'dipinjam' THEN 1 ELSE 0 END) AS alat_dipinjam,
  SUM(CASE WHEN a.status = 'rusak' THEN 1 ELSE 0 END) AS alat_rusak
FROM kategori k
LEFT JOIN alat a ON a.kategori_id = k.id
GROUP BY k.id;

-- ============================================
-- STORED PROCEDURES (Optional)
-- ============================================

DELIMITER $$

-- Procedure: Hitung total denda
CREATE PROCEDURE IF NOT EXISTS `sp_hitung_denda`(
  IN p_pengembalian_id BIGINT,
  OUT p_total_denda DECIMAL(10,2)
)
BEGIN
  DECLARE v_hari_terlambat INT DEFAULT 0;
  DECLARE v_denda_telat DECIMAL(10,2) DEFAULT 0;
  DECLARE v_denda_rusak DECIMAL(10,2) DEFAULT 0;
  DECLARE v_denda_hilang DECIMAL(10,2) DEFAULT 0;
  
  -- Hitung hari terlambat
  SELECT GREATEST(0, DATEDIFF(pen.tanggal_kembali_aktual, p.tanggal_kembali))
  INTO v_hari_terlambat
  FROM pengembalian pen
  JOIN peminjaman p ON p.id = pen.peminjaman_id
  WHERE pen.id = p_pengembalian_id;
  
  -- Denda keterlambatan (Rp 10.000/hari)
  SET v_denda_telat = v_hari_terlambat * 10000;
  
  -- Denda rusak dan hilang
  SELECT 
    SUM(denda_rusak) + SUM(denda_hilang)
  INTO v_denda_rusak
  FROM detail_pengembalian
  WHERE pengembalian_id = p_pengembalian_id;
  
  -- Total denda
  SET p_total_denda = v_denda_telat + IFNULL(v_denda_rusak, 0);
END$$

DELIMITER ;

-- ============================================
-- TRIGGERS (Optional - untuk audit trail)
-- ============================================

DELIMITER $$

-- Trigger: Log saat user dibuat
CREATE TRIGGER IF NOT EXISTS `trg_users_after_insert`
AFTER INSERT ON `users`
FOR EACH ROW
BEGIN
  INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, created_at, updated_at)
  VALUES (NEW.id, 'User Created', CONCAT('User baru: ', NEW.name, ' (', NEW.email, ')'), NOW(), NOW());
END$$

-- Trigger: Log saat peminjaman dibuat
CREATE TRIGGER IF NOT EXISTS `trg_peminjaman_after_insert`
AFTER INSERT ON `peminjaman`
FOR EACH ROW
BEGIN
  INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, created_at, updated_at)
  VALUES (NEW.user_id, 'Peminjaman Created', CONCAT('Peminjaman baru #', NEW.id), NOW(), NOW());
END$$

-- Trigger: Log saat peminjaman diupdate
CREATE TRIGGER IF NOT EXISTS `trg_peminjaman_after_update`
AFTER UPDATE ON `peminjaman`
FOR EACH ROW
BEGIN
  IF OLD.status != NEW.status THEN
    INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, created_at, updated_at)
    VALUES (NEW.user_id, 'Peminjaman Status Changed', 
            CONCAT('Peminjaman #', NEW.id, ' status: ', OLD.status, ' → ', NEW.status), 
            NOW(), NOW());
  END IF;
END$$

DELIMITER ;

-- ============================================
-- INDEXES TAMBAHAN (untuk optimasi query)
-- ============================================

-- Index untuk pencarian
ALTER TABLE `alat` ADD FULLTEXT INDEX `alat_nama_deskripsi_fulltext` (`nama`, `deskripsi`);
ALTER TABLE `users` ADD INDEX `users_name_index` (`name`);

-- ============================================
-- SELESAI
-- ============================================

-- Tampilkan summary
SELECT 'Database schema created successfully!' AS status;
SELECT COUNT(*) AS total_tables FROM information_schema.tables 
WHERE table_schema = 'peminjaman_alat' AND table_type = 'BASE TABLE';
