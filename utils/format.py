from datetime import date, datetime


def rupiah(angka) -> str:
    try:
        n = float(angka or 0)
        return f"Rp {n:,.0f}".replace(",", ".")
    except Exception:
        return "Rp 0"


def tgl(dt) -> str:
    if dt is None:
        return "-"
    if isinstance(dt, str):
        try:
            dt = date.fromisoformat(dt[:10])
        except Exception:
            return str(dt)
    try:
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(dt)


def status_color(status: str) -> str:
    mapping = {
        'pending':     '#D97706',
        'disetujui':   '#16A34A',
        'ditolak':     '#DC2626',
        'selesai':     '#2563EB',
        'belum_bayar': '#DC2626',
        'lunas':       '#16A34A',
        'tersedia':    '#16A34A',
        'dipinjam':    '#D97706',
        'rusak':       '#DC2626',
        'hilang':      '#7C3AED',
        'mixed':       '#0891B2',
        'baik':        '#16A34A',
    }
    return mapping.get(str(status).lower(), '#94A3B8')


def status_label(status: str) -> str:
    mapping = {
        'pending':     'Pending',
        'disetujui':   'Disetujui',
        'ditolak':     'Ditolak',
        'selesai':     'Selesai',
        'belum_bayar': 'Belum Bayar',
        'lunas':       'Lunas',
        'tersedia':    'Tersedia',
        'dipinjam':    'Dipinjam',
        'rusak':       'Rusak',
        'hilang':      'Hilang',
        'mixed':       'Campuran',
        'baik':        'Baik',
    }
    return mapping.get(str(status).lower(), status.title())


def tgl_waktu(dt) -> str:
    """Format datetime ke dd/mm/yyyy HH:MM"""
    if dt is None:
        return "-"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except Exception:
            return str(dt)
    try:
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return str(dt)
