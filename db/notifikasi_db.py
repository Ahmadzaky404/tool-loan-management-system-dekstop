from db.connection import Database


def get_notifikasi(user_id, hanya_unread=False):
    cur = Database.cursor()
    sql = "SELECT * FROM notifications WHERE user_id=%s"
    params = [user_id]
    if hanya_unread:
        sql += " AND is_read=0"
    sql += " ORDER BY created_at DESC LIMIT 50"
    cur.execute(sql, params)
    return cur.fetchall()


def count_unread(user_id):
    cur = Database.cursor()
    cur.execute(
        "SELECT COUNT(*) AS total FROM notifications WHERE user_id=%s AND is_read=0",
        (user_id,)
    )
    row = cur.fetchone()
    return row['total'] if row else 0


def tandai_dibaca(notif_id):
    cur = Database.cursor()
    cur.execute("UPDATE notifications SET is_read=1, updated_at=NOW() WHERE id=%s", (notif_id,))
    Database.commit()


def tandai_semua_dibaca(user_id):
    cur = Database.cursor()
    cur.execute(
        "UPDATE notifications SET is_read=1, updated_at=NOW() WHERE user_id=%s AND is_read=0",
        (user_id,)
    )
    Database.commit()
