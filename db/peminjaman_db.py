from db.connection import Database


def get_peminjaman(user_id=None, role=None, status='', search=''):
    cur = Database.cursor()
    sql = """
        SELECT p.*, u.name AS nama_peminjam, ap.name AS nama_approver,
               GROUP_CONCAT(a.nama, ' (', dp.jumlah, ')' SEPARATOR ', ') AS daftar_alat
        FROM peminjaman p
        JOIN users u ON u.id = p.user_id
        LEFT JOIN users ap ON ap.id = p.approved_by
        LEFT JOIN detail_peminjaman dp ON dp.peminjaman_id = p.id
        LEFT JOIN alat a ON a.id = dp.alat_id
        WHERE p.deleted_at IS NULL
    """
    params = []
    if role == 'peminjam' and user_id:
        sql += " AND p.user_id = %s"
        params.append(user_id)
    if status:
        sql += " AND p.status = %s"
        params.append(status)
    if search:
        sql += " AND u.name LIKE %s"
        params.append(f"%{search}%")
    sql += " GROUP BY p.id ORDER BY p.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()


def get_peminjaman_by_id(pid):
    cur = Database.cursor()
    cur.execute("""
        SELECT p.*, u.name AS nama_peminjam, ap.name AS nama_approver
        FROM peminjaman p
        JOIN users u ON u.id = p.user_id
        LEFT JOIN users ap ON ap.id = p.approved_by
        WHERE p.id = %s AND p.deleted_at IS NULL
    """, (pid,))
    return cur.fetchone()


def get_detail_peminjaman(pid):
    cur = Database.cursor()
    cur.execute("""
        SELECT dp.*, a.nama AS alat_nama, a.kode, k.nama AS kategori
        FROM detail_peminjaman dp
        JOIN alat a ON a.id = dp.alat_id
        JOIN kategori k ON k.id = a.kategori_id
        WHERE dp.peminjaman_id = %s
    """, (pid,))
    return cur.fetchall()


def get_peminjaman_disetujui_tanpa_kembali(user_id=None, role=None):
    """Ambil peminjaman yg sudah disetujui tapi belum ada pengembalian"""
    cur = Database.cursor()
    sql = """
        SELECT p.*, u.name AS nama_peminjam
        FROM peminjaman p
        JOIN users u ON u.id = p.user_id
        LEFT JOIN pengembalian pen ON pen.peminjaman_id = p.id
        WHERE p.status = 'disetujui' AND pen.id IS NULL AND p.deleted_at IS NULL
    """
    params = []
    if role == 'peminjam' and user_id:
        sql += " AND p.user_id = %s"
        params.append(user_id)
    sql += " ORDER BY p.tanggal_kembali ASC"
    cur.execute(sql, params)
    return cur.fetchall()


def insert_peminjaman(user_id, tgl_pinjam, tgl_kembali, items: list):
    conn = Database.get_connection()
    cur = Database.cursor()
    try:
        # Pastikan tidak ada transaksi yang tertinggal
        try:
            conn.rollback()
        except:
            pass
        
        conn.start_transaction()
        for item in items:
            cur.execute("SELECT nama, stok FROM alat WHERE id=%s FOR UPDATE", (item['alat_id'],))
            a = cur.fetchone()
            if not a:
                conn.rollback()
                return False, f"Alat tidak ditemukan"
            if a['stok'] < item['jumlah']:
                conn.rollback()
                return False, f"Stok {a['nama']} tidak cukup (tersedia: {a['stok']})"

        cur.execute("""
            INSERT INTO peminjaman (user_id, tanggal_pinjam, tanggal_kembali, status, created_at, updated_at)
            VALUES (%s, %s, %s, 'pending', NOW(), NOW())
        """, (user_id, tgl_pinjam, tgl_kembali))
        pid = cur.lastrowid

        for item in items:
            cur.execute("""
                INSERT INTO detail_peminjaman (peminjaman_id, alat_id, jumlah, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
            """, (pid, item['alat_id'], item['jumlah']))

        # Notif ke admin & petugas
        cur.execute(
            "SELECT u.id FROM users u JOIN roles r ON r.id=u.role_id "
            "WHERE r.name IN ('admin','petugas') AND u.is_active=1"
        )
        for adm in cur.fetchall():
            cur.execute("""
                INSERT INTO notifications (user_id, title, message, type, is_read, created_at, updated_at)
                VALUES (%s,'Peminjaman Baru',%s,'info',0,NOW(),NOW())
            """, (adm['id'], f"Pengajuan peminjaman baru #{pid} dari user #{user_id}"))

        # Log
        cur.execute("""
            INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, ip_address, user_agent, created_at, updated_at)
            VALUES (%s,'Create Peminjaman',%s,'127.0.0.1','Desktop App',NOW(),NOW())
        """, (user_id, f"Mengajukan peminjaman baru #{pid}"))

        conn.commit()
        return True, pid
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)


def approve_peminjaman(pid, approved_by):
    conn = Database.get_connection()
    cur = Database.cursor()
    try:
        # Pastikan tidak ada transaksi yang tertinggal
        try:
            conn.rollback()
        except:
            pass
        
        conn.start_transaction()
        cur.execute(
            "SELECT * FROM peminjaman WHERE id=%s AND status='pending' AND deleted_at IS NULL FOR UPDATE",
            (pid,)
        )
        p = cur.fetchone()
        if not p:
            conn.rollback()
            return False, "Peminjaman tidak valid atau bukan status pending"

        cur.execute("""
            UPDATE peminjaman SET status='disetujui', approved_by=%s, updated_at=NOW() WHERE id=%s
        """, (approved_by, pid))

        cur.execute("SELECT alat_id, jumlah FROM detail_peminjaman WHERE peminjaman_id=%s", (pid,))
        for d in cur.fetchall():
            cur.execute("UPDATE alat SET stok=stok-%s, updated_at=NOW() WHERE id=%s", (d['jumlah'], d['alat_id']))

        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at, updated_at)
            VALUES (%s,'Peminjaman Disetujui',%s,'success',0,NOW(),NOW())
        """, (p['user_id'], f"Peminjaman #{pid} telah disetujui"))

        cur.execute("""
            INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, ip_address, user_agent, created_at, updated_at)
            VALUES (%s,'Approve Peminjaman',%s,'127.0.0.1','Desktop App',NOW(),NOW())
        """, (approved_by, f"Menyetujui peminjaman #{pid}"))

        conn.commit()
        return True, "Peminjaman berhasil disetujui"
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)


def reject_peminjaman(pid, alasan, rejected_by):
    conn = Database.get_connection()
    cur = Database.cursor()
    try:
        # Pastikan tidak ada transaksi yang tertinggal
        try:
            conn.rollback()
        except:
            pass
        
        conn.start_transaction()
        cur.execute(
            "SELECT * FROM peminjaman WHERE id=%s AND status='pending' AND deleted_at IS NULL",
            (pid,)
        )
        p = cur.fetchone()
        if not p:
            conn.rollback()
            return False, "Peminjaman tidak valid"

        cur.execute("""
            UPDATE peminjaman SET status='ditolak', alasan_penolakan=%s, approved_by=%s, updated_at=NOW()
            WHERE id=%s
        """, (alasan, rejected_by, pid))

        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at, updated_at)
            VALUES (%s,'Peminjaman Ditolak',%s,'error',0,NOW(),NOW())
        """, (p['user_id'], f"Peminjaman #{pid} ditolak. Alasan: {alasan}"))

        conn.commit()
        return True, "Peminjaman berhasil ditolak"
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)


def count_peminjaman_stats():
    cur = Database.cursor()
    cur.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status='pending') AS pending,
            SUM(status='disetujui') AS disetujui,
            SUM(status='ditolak') AS ditolak,
            SUM(status='selesai') AS selesai
        FROM peminjaman WHERE deleted_at IS NULL
    """)
    return cur.fetchone()
