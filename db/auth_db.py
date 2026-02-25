from db.connection import Database


def get_user_by_email(email: str):
    cur = Database.cursor()
    cur.execute("""
        SELECT u.id, u.name, u.email, u.password, u.is_active,
               r.id AS role_id, r.name AS role_name
        FROM users u
        JOIN roles r ON r.id = u.role_id
        WHERE u.email = %s
    """, (email,))
    return cur.fetchone()
