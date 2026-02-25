
# ── Konfigurasi MySQL ─────────────────────────────────
DB_CONFIG = {
    'host':     '127.0.0.1',
    'port':     3306,
    'database': 'peminjaman_alat',
    'user':     'root',
    'password': '',
    'charset':  'utf8mb4',
    'autocommit': False,
    'connection_timeout': 10,
}

# ── Tarif Denda ───────────────────────────────────────
TARIF_KETERLAMBATAN = 10_000
TARIF_RUSAK         = 50_000
TARIF_HILANG        = 500_000

# ── App Info ──────────────────────────────────────────
APP_NAME    = "Peminjaman Alat"
APP_VERSION = "1.0.0"
WINDOW_SIZE = "1280x740"
MIN_SIZE    = (1100, 650)

# ── Load Theme dari file ──────────────────────────────
import json
import os

def load_theme():
    try:
        if os.path.exists('theme_config.json'):
            with open('theme_config.json', 'r') as f:
                return json.load(f).get('theme', 'dark')
    except:
        pass
    return 'dark'

def save_theme(theme_name):
    try:
        with open('theme_config.json', 'w') as f:
            json.dump({'theme': theme_name}, f)
    except:
        pass

CURRENT_THEME = load_theme()

# ── Dark Theme Colors ─────────────────────────────────
DARK_THEME = {
    'SIDEBAR_BG':   "#0F172A",
    'TOPBAR_BG':    "#1E293B",
    'CONTENT_BG':   "#0F172A",
    'CARD_BG':      "#1E293B",
    'CARD_BORDER':  "#334155",
    'INPUT_BG':     "#1E293B",
    'TABLE_BG':     "#1E293B",
    'TABLE_ROW':    "#263348",
    'TABLE_SEL':    "#2563EB",
    'TEXT_PRIMARY': "#F1F5F9",
    'TEXT_MUTED':   "#94A3B8",
    'TEXT_LABEL':   "#CBD5E1",
}

# ── Light Theme Colors ────────────────────────────────
LIGHT_THEME = {
    'SIDEBAR_BG':   "#FFFFFF",
    'TOPBAR_BG':    "#F8FAFC",
    'CONTENT_BG':   "#F1F5F9",
    'CARD_BG':      "#FFFFFF",
    'CARD_BORDER':  "#E2E8F0",
    'INPUT_BG':     "#FFFFFF",
    'TABLE_BG':     "#FFFFFF",
    'TABLE_ROW':    "#F8FAFC",
    'TABLE_SEL':    "#2563EB",
    'TEXT_PRIMARY': "#0F172A",
    'TEXT_MUTED':   "#64748B",
    'TEXT_LABEL':   "#475569",
}

# ── Warna Tetap (tidak berubah) ───────────────────────
PRIMARY      = "#2563EB"
PRIMARY_HV   = "#1D4ED8"
SUCCESS      = "#16A34A"
DANGER       = "#DC2626"
WARNING      = "#D97706"
INFO         = "#0891B2"
FONT_FAMILY  = "Helvetica"

# ── Apply Theme ───────────────────────────────────────
theme = LIGHT_THEME if CURRENT_THEME == "light" else DARK_THEME

SIDEBAR_BG   = theme['SIDEBAR_BG']
TOPBAR_BG    = theme['TOPBAR_BG']
CONTENT_BG   = theme['CONTENT_BG']
CARD_BG      = theme['CARD_BG']
CARD_BORDER  = theme['CARD_BORDER']
INPUT_BG     = theme['INPUT_BG']
TABLE_BG     = theme['TABLE_BG']
TABLE_ROW    = theme['TABLE_ROW']
TABLE_SEL    = theme['TABLE_SEL']
TEXT_PRIMARY = theme['TEXT_PRIMARY']
TEXT_MUTED   = theme['TEXT_MUTED']
TEXT_LABEL   = theme['TEXT_LABEL']

