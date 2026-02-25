import bcrypt
from db.auth_db import get_user_by_email

# ── Session Global ──────────────────────────────────
_current_user: dict | None = None


def login(email: str, password: str):
    global _current_user
    user = get_user_by_email(email)
    if not user:
        return False, "Email tidak ditemukan"
    if not user['is_active']:
        return False, "Akun Anda dinonaktifkan. Hubungi administrator."
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            _current_user = user
            return True, user
        return False, "Password salah"
    except Exception:
        return False, "Terjadi kesalahan saat verifikasi password"


def logout():
    global _current_user
    _current_user = None


def current_user():
    return _current_user


def is_admin():
    return _current_user is not None and _current_user.get('role_name') == 'admin'


def is_petugas():
    return _current_user is not None and _current_user.get('role_name') == 'petugas'


def is_peminjam():
    return _current_user is not None and _current_user.get('role_name') == 'peminjam'


def is_admin_or_petugas():
    return is_admin() or is_petugas()
