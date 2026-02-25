from db.connection import Database


def get_denda(user_id=None, role=None, status=''):
    cur = Database.cursor()
    sql = """
        SELECT d.*, u.name AS nama_peminjam, p.id AS peminjaman_id,
               pen.tanggal_kembali_aktual
        FROM denda d
        JOIN pengembalian pen ON pen.id = d.pengembalian_id
        JOIN peminjaman p ON p.id = pen.peminjaman_id
        JOIN users u ON u.id = p.user_id
        WHERE 1=1
    """
    params = []
    if role == 'peminjam' and user_id:
        sql += " AND p.user_id=%s"
        params.append(user_id)
    if status:
        sql += " AND d.status=%s"
        params.append(status)
    sql += " ORDER BY d.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()


def bayar_denda(denda_id, metode, bukti=''):
    cur = Database.cursor()
    cur.execute("""
        UPDATE denda SET status='lunas', metode_pembayaran=%s, bukti_pembayaran=%s,
        tanggal_bayar=NOW(), updated_at=NOW()
        WHERE id=%s AND status='belum_bayar'
    """, (metode, bukti, denda_id))
    Database.commit()
    return cur.rowcount > 0


def count_denda_stats():
    cur = Database.cursor()
    cur.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status='belum_bayar') AS belum_bayar,
            SUM(status='lunas') AS lunas,
            SUM(jumlah) AS total_nominal,
            SUM(CASE WHEN status='belum_bayar' THEN jumlah ELSE 0 END) AS nominal_belum_bayar
        FROM denda
    """)
    return cur.fetchone()
