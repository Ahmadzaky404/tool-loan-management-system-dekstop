from db.connection import Database
from datetime import date


def get_laporan_peminjaman(tgl_dari=None, tgl_sampai=None, status=None):
    """Laporan peminjaman dengan filter tanggal dan status"""
    cur = Database.cursor()
    sql = """
        SELECT p.*, u.name AS nama_peminjam, u.email,
               a.name AS nama_approver,
               GROUP_CONCAT(CONCAT(al.nama, ' (', dp.jumlah, 'x)') SEPARATOR ', ') AS alat_list
        FROM peminjaman p
        JOIN users u ON u.id = p.user_id
        LEFT JOIN users a ON a.id = p.approved_by
        LEFT JOIN detail_peminjaman dp ON dp.peminjaman_id = p.id
        LEFT JOIN alat al ON al.id = dp.alat_id
        WHERE p.deleted_at IS NULL
    """
    params = []
    
    if tgl_dari:
        sql += " AND p.tanggal_pinjam >= %s"
        params.append(tgl_dari)
    if tgl_sampai:
        sql += " AND p.tanggal_pinjam <= %s"
        params.append(tgl_sampai)
    if status and status != 'semua':
        sql += " AND p.status = %s"
        params.append(status)
    
    sql += " GROUP BY p.id ORDER BY p.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()


def get_laporan_pengembalian(tgl_dari=None, tgl_sampai=None):
    """Laporan pengembalian dengan filter tanggal"""
    cur = Database.cursor()
    sql = """
        SELECT pen.*, p.tanggal_pinjam, p.tanggal_kembali,
               u.name AS nama_peminjam, u.email,
               v.name AS nama_verifikator,
               GROUP_CONCAT(
                   CONCAT(a.nama, ' - Baik:', dp.jumlah_baik, ' Rusak:', dp.jumlah_rusak, ' Hilang:', dp.jumlah_hilang)
                   SEPARATOR ' | '
               ) AS detail_kondisi,
               COALESCE(d.jumlah, 0) AS total_denda
        FROM pengembalian pen
        JOIN peminjaman p ON p.id = pen.peminjaman_id
        JOIN users u ON u.id = p.user_id
        LEFT JOIN users v ON v.id = pen.verified_by
        LEFT JOIN detail_pengembalian dp ON dp.pengembalian_id = pen.id
        LEFT JOIN alat a ON a.id = dp.alat_id
        LEFT JOIN denda d ON d.pengembalian_id = pen.id
        WHERE 1=1
    """
    params = []
    
    if tgl_dari:
        sql += " AND pen.tanggal_kembali_aktual >= %s"
        params.append(tgl_dari)
    if tgl_sampai:
        sql += " AND pen.tanggal_kembali_aktual <= %s"
        params.append(tgl_sampai)
    
    sql += " GROUP BY pen.id ORDER BY pen.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()


def get_laporan_denda(tgl_dari=None, tgl_sampai=None, status_bayar=None):
    """Laporan denda dengan filter tanggal dan status bayar"""
    cur = Database.cursor()
    sql = """
        SELECT d.*, pen.tanggal_kembali_aktual,
               p.tanggal_pinjam, p.tanggal_kembali,
               u.name AS nama_peminjam, u.email
        FROM denda d
        JOIN pengembalian pen ON pen.id = d.pengembalian_id
        JOIN peminjaman p ON p.id = pen.peminjaman_id
        JOIN users u ON u.id = p.user_id
        WHERE 1=1
    """
    params = []
    
    if tgl_dari:
        sql += " AND d.created_at >= %s"
        params.append(tgl_dari)
    if tgl_sampai:
        sql += " AND d.created_at <= %s"
        params.append(tgl_sampai)
    if status_bayar and status_bayar != 'semua':
        sql += " AND d.status = %s"
        params.append(status_bayar)
    
    sql += " ORDER BY d.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()
