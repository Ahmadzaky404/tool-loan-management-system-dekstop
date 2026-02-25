from db.connection import Database


# ── Kategori ──────────────────────────────────────────
def get_all_kategori():
    cur = Database.cursor()
    cur.execute("SELECT * FROM kategori ORDER BY nama")
    return cur.fetchall()

def insert_kategori(nama, deskripsi=''):
    cur = Database.cursor()
    cur.execute(
        "INSERT INTO kategori (nama, deskripsi, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())",
        (nama, deskripsi)
    )
    Database.commit()

def update_kategori(kid, nama, deskripsi=''):
    cur = Database.cursor()
    cur.execute(
        "UPDATE kategori SET nama=%s, deskripsi=%s, updated_at=NOW() WHERE id=%s",
        (nama, deskripsi, kid)
    )
    Database.commit()

def delete_kategori(kid):
    cur = Database.cursor()
    cur.execute("DELETE FROM kategori WHERE id=%s", (kid,))
    Database.commit()


# ── Alat ──────────────────────────────────────────────
def get_all_alat(search='', status=''):
    cur = Database.cursor()
    sql = """
        SELECT a.*, k.nama AS kategori_nama
        FROM alat a JOIN kategori k ON k.id = a.kategori_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (a.nama LIKE %s OR a.kode LIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    if status:
        sql += " AND a.status = %s"
        params.append(status)
    sql += " ORDER BY a.nama"
    cur.execute(sql, params)
    return cur.fetchall()

def get_alat_tersedia():
    cur = Database.cursor()
    cur.execute("""
        SELECT a.*, k.nama AS kategori_nama
        FROM alat a JOIN kategori k ON k.id = a.kategori_id
        WHERE a.status = 'tersedia' AND a.stok > 0
        ORDER BY a.nama
    """)
    return cur.fetchall()

def get_alat_by_id(alat_id):
    cur = Database.cursor()
    cur.execute("""
        SELECT a.*, k.nama AS kategori_nama
        FROM alat a JOIN kategori k ON k.id = a.kategori_id
        WHERE a.id = %s
    """, (alat_id,))
    return cur.fetchone()

def insert_alat(data: dict):
    cur = Database.cursor()
    cur.execute("""
        INSERT INTO alat (kategori_id, nama, kode, deskripsi, stok, status, created_at, updated_at)
        VALUES (%(kategori_id)s, %(nama)s, %(kode)s, %(deskripsi)s, %(stok)s, 'tersedia', NOW(), NOW())
    """, data)
    Database.commit()
    return cur.lastrowid

def update_alat(alat_id, data: dict):
    cur = Database.cursor()
    cur.execute("""
        UPDATE alat SET kategori_id=%(kategori_id)s, nama=%(nama)s, kode=%(kode)s,
        deskripsi=%(deskripsi)s, stok=%(stok)s, updated_at=NOW()
        WHERE id=%(id)s
    """, {**data, 'id': alat_id})
    Database.commit()

def delete_alat(alat_id):
    cur = Database.cursor()
    cur.execute("DELETE FROM alat WHERE id=%s", (alat_id,))
    Database.commit()

def count_alat_stats():
    cur = Database.cursor()
    cur.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(status='tersedia') AS tersedia,
            SUM(status='dipinjam') AS dipinjam,
            SUM(status='rusak') AS rusak
        FROM alat
    """)
    return cur.fetchone()
