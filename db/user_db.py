from db.connection import Database


def get_all_users(search=''):
    cur = Database.cursor()
    sql = """
        SELECT u.*, r.name AS role_name
        FROM users u JOIN roles r ON r.id = u.role_id
        WHERE 1=1
    """
    params = []
    if search:
        sql += " AND (u.name LIKE %s OR u.email LIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    sql += " ORDER BY u.name"
    cur.execute(sql, params)
    return cur.fetchall()


def get_all_roles():
    cur = Database.cursor()
    cur.execute("SELECT * FROM roles ORDER BY id")
    return cur.fetchall()


def insert_user(data: dict):
    import bcrypt
    hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    cur = Database.cursor()
    cur.execute("""
        INSERT INTO users (name, email, password, role_id, is_active, created_at, updated_at)
        VALUES (%(name)s, %(email)s, %(password)s, %(role_id)s, 1, NOW(), NOW())
    """, {**data, 'password': hashed})
    Database.commit()


def update_user(uid, data: dict):
    cur = Database.cursor()
    if data.get('password'):
        import bcrypt
        hashed = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
        cur.execute("""
            UPDATE users SET name=%(name)s, email=%(email)s, password=%(password)s,
            role_id=%(role_id)s, updated_at=NOW() WHERE id=%(id)s
        """, {**data, 'password': hashed, 'id': uid})
    else:
        cur.execute("""
            UPDATE users SET name=%(name)s, email=%(email)s, role_id=%(role_id)s,
            updated_at=NOW() WHERE id=%(id)s
        """, {**data, 'id': uid})
    Database.commit()


def toggle_user_status(uid):
    cur = Database.cursor()
    cur.execute(
        "UPDATE users SET is_active = NOT is_active, updated_at=NOW() WHERE id=%s",
        (uid,)
    )
    Database.commit()


def delete_user(uid):
    cur = Database.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (uid,))
    Database.commit()


def get_log_aktivitas(limit=100):
    cur = Database.cursor()
    cur.execute("""
        SELECT la.*, u.name AS nama_user
        FROM log_aktivitas la
        JOIN users u ON u.id = la.user_id
        ORDER BY la.created_at DESC
        LIMIT %s
    """, (limit,))
    return cur.fetchall()
