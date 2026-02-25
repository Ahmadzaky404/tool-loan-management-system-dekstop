from db.connection import Database
from config import TARIF_KETERLAMBATAN, TARIF_RUSAK, TARIF_HILANG
from datetime import date as Date


def get_pengembalian(user_id=None, role=None):
    cur = Database.cursor()
    sql = """
        SELECT pen.*, p.tanggal_pinjam, p.tanggal_kembali, p.user_id,
               u.name AS nama_peminjam, v.name AS nama_verifikator
        FROM pengembalian pen
        JOIN peminjaman p ON p.id = pen.peminjaman_id
        JOIN users u ON u.id = p.user_id
        LEFT JOIN users v ON v.id = pen.verified_by
        WHERE 1=1
    """
    params = []
    if role == 'peminjam' and user_id:
        sql += " AND p.user_id=%s"
        params.append(user_id)
    sql += " ORDER BY pen.created_at DESC"
    cur.execute(sql, params)
    return cur.fetchall()


def get_detail_pengembalian(pengembalian_id):
    cur = Database.cursor()
    cur.execute("""
        SELECT dp.*, a.nama AS alat_nama, a.kode
        FROM detail_pengembalian dp
        JOIN alat a ON a.id = dp.alat_id
        WHERE dp.pengembalian_id = %s
    """, (pengembalian_id,))
    return cur.fetchall()


def insert_pengembalian(peminjaman_id, tgl_aktual, kondisi: dict, catatan=''):
    """kondisi = {alat_id: {'baik': x, 'rusak': y, 'hilang': z}}"""
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
            "SELECT alat_id, jumlah FROM detail_peminjaman WHERE peminjaman_id=%s",
            (peminjaman_id,)
        )
        details = cur.fetchall()
        for d in details:
            k = kondisi.get(d['alat_id'], {})
            total = k.get('baik', 0) + k.get('rusak', 0) + k.get('hilang', 0)
            if total != d['jumlah']:
                conn.rollback()
                return False, f"Total kondisi alat ID {d['alat_id']} harus {d['jumlah']}, dapat {total}"

        cur.execute("""
            INSERT INTO pengembalian (peminjaman_id, tanggal_kembali_aktual, kondisi_alat, catatan, created_at, updated_at)
            VALUES (%s, %s, 'mixed', %s, NOW(), NOW())
        """, (peminjaman_id, tgl_aktual, catatan))
        pen_id = cur.lastrowid

        for d in details:
            k = kondisi.get(d['alat_id'], {'baik': 0, 'rusak': 0, 'hilang': 0})
            cur.execute("""
                INSERT INTO detail_pengembalian
                (pengembalian_id, alat_id, jumlah_baik, jumlah_rusak, jumlah_hilang, denda_rusak, denda_hilang, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,0,0,NOW(),NOW())
            """, (pen_id, d['alat_id'], k['baik'], k['rusak'], k['hilang']))

        conn.commit()
        return True, pen_id
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        return False, str(e)


def verifikasi_pengembalian(pengembalian_id, verified_by, denda_manual=None):
    conn = Database.get_connection()
    cur = Database.cursor()
    try:
        # Pastikan tidak ada transaksi yang tertinggal
        try:
            conn.rollback()
        except:
            pass
        
        conn.start_transaction()

        cur.execute("""
            SELECT pen.*, p.tanggal_kembali, p.user_id, p.id AS peminjaman_id
            FROM pengembalian pen
            JOIN peminjaman p ON p.id = pen.peminjaman_id
            WHERE pen.id = %s
        """, (pengembalian_id,))
        pen = cur.fetchone()
        if not pen:
            conn.rollback()
            return False, "Data pengembalian tidak ditemukan"

        cur.execute("""
            SELECT dp.*, a.nama AS alat_nama
            FROM detail_pengembalian dp
            JOIN alat a ON a.id = dp.alat_id
            WHERE dp.pengembalian_id = %s
        """, (pengembalian_id,))
        details = cur.fetchall()

        total_denda = 0
        keterangan_list = []

        # Denda keterlambatan
        tgl_janji  = pen.get('tanggal_kembali')
        tgl_aktual = pen.get('tanggal_kembali_aktual')
        
        if tgl_janji and tgl_aktual:
            if isinstance(tgl_janji, str):
                tgl_janji = Date.fromisoformat(tgl_janji)
            if isinstance(tgl_aktual, str):
                tgl_aktual = Date.fromisoformat(tgl_aktual)

            if tgl_aktual > tgl_janji:
                hari = (tgl_aktual - tgl_janji).days
                d_telat = hari * TARIF_KETERLAMBATAN
                total_denda += d_telat
                keterangan_list.append(f"Keterlambatan {hari} hari: Rp {d_telat:,.0f}")

        for d in details:
            alat_id = d['alat_id']
            d_rusak = d_hilang = 0

            if d['jumlah_rusak'] > 0:
                if denda_manual and alat_id in denda_manual:
                    d_rusak = float(denda_manual[alat_id].get('rusak', d['jumlah_rusak'] * TARIF_RUSAK))
                else:
                    d_rusak = d['jumlah_rusak'] * TARIF_RUSAK
                if d_rusak > 0:
                    keterangan_list.append(f"{d['alat_nama']} rusak ({d['jumlah_rusak']}x): Rp {d_rusak:,.0f}")

            if d['jumlah_hilang'] > 0:
                if denda_manual and alat_id in denda_manual:
                    d_hilang = float(denda_manual[alat_id].get('hilang', d['jumlah_hilang'] * TARIF_HILANG))
                else:
                    d_hilang = d['jumlah_hilang'] * TARIF_HILANG
                if d_hilang > 0:
                    keterangan_list.append(f"{d['alat_nama']} hilang ({d['jumlah_hilang']}x): Rp {d_hilang:,.0f}")

            total_denda += d_rusak + d_hilang

            cur.execute("""
                UPDATE detail_pengembalian SET denda_rusak=%s, denda_hilang=%s, updated_at=NOW()
                WHERE id=%s
            """, (d_rusak, d_hilang, d['id']))

            stok_kembali = d['jumlah_baik'] + d['jumlah_rusak']
            cur.execute("UPDATE alat SET stok=stok+%s, updated_at=NOW() WHERE id=%s", (stok_kembali, alat_id))

            if d['jumlah_baik'] > 0:
                status_alat = 'tersedia'
            elif d['jumlah_rusak'] > 0:
                status_alat = 'rusak'
            else:
                status_alat = 'tersedia'
            cur.execute("UPDATE alat SET status=%s, updated_at=NOW() WHERE id=%s", (status_alat, alat_id))

        cur.execute("UPDATE pengembalian SET verified_by=%s, updated_at=NOW() WHERE id=%s", (verified_by, pengembalian_id))
        cur.execute("UPDATE peminjaman SET status='selesai', updated_at=NOW() WHERE id=%s", (pen['peminjaman_id'],))

        if total_denda > 0:
            ket = ' | '.join(keterangan_list)
            cur.execute("""
                INSERT INTO denda (pengembalian_id, jumlah, keterangan, status, created_at, updated_at)
                VALUES (%s,%s,%s,'belum_bayar',NOW(),NOW())
            """, (pengembalian_id, total_denda, ket))
            cur.execute("""
                INSERT INTO notifications (user_id, title, message, type, is_read, created_at, updated_at)
                VALUES (%s,'Ada Denda',%s,'warning',0,NOW(),NOW())
            """, (pen['user_id'], f"Anda memiliki denda sebesar Rp {total_denda:,.0f}"))

        cur.execute("""
            INSERT INTO notifications (user_id, title, message, type, is_read, created_at, updated_at)
            VALUES (%s,'Pengembalian Diverifikasi',%s,'success',0,NOW(),NOW())
        """, (pen['user_id'], f"Pengembalian peminjaman #{pen['peminjaman_id']} telah diverifikasi"))

        cur.execute("""
            INSERT INTO log_aktivitas (user_id, aktivitas, deskripsi, ip_address, user_agent, created_at, updated_at)
            VALUES (%s,'Verifikasi Pengembalian',%s,'127.0.0.1','Desktop App',NOW(),NOW())
        """, (verified_by, f"Memverifikasi pengembalian #{pengembalian_id}, denda Rp {total_denda:,.0f}"))

        conn.commit()
        return True, total_denda
    except Exception as e:
        conn.rollback()
        return False, str(e)
