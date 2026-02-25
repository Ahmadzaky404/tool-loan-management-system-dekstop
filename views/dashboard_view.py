import customtkinter as ctk
from config import *
from components.widgets import StatCard, SectionHeader, DataTable
from db.alat_db import count_alat_stats
from db.peminjaman_db import count_peminjaman_stats, get_peminjaman
from db.denda_db import count_denda_stats
from utils.auth import is_admin, is_admin_or_petugas, is_peminjam
from utils.format import rupiah, tgl, status_label, status_color


class DashboardView(ctk.CTkScrollableFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent", scrollbar_button_color=CARD_BG)
        self.user = user
        self._build()

    def _build(self):
        role = self.user['role_name']

        # Greeting
        ctk.CTkLabel(self, text=f"Halo, {self.user['name']} 👋",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self, text=f"Role: {self.user['role_name'].title()}  •  Selamat datang kembali",
                     font=ctk.CTkFont(size=13), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        # Stats
        if role in ('admin', 'petugas'):
            self._build_admin_stats()
        else:
            self._build_peminjam_stats()

        # Recent peminjaman
        self._build_recent_table(role)

    def _build_admin_stats(self):
        alat   = count_alat_stats()   or {}
        pinjam = count_peminjaman_stats() or {}
        denda  = count_denda_stats()  or {}

        cards_data = [
            ("Total Alat",        alat.get('total', 0),        "🔧", PRIMARY),
            ("Alat Tersedia",     alat.get('tersedia', 0),      "✅", SUCCESS),
            ("Alat Dipinjam",     alat.get('dipinjam', 0),      "📦", WARNING),
            ("Alat Rusak",        alat.get('rusak', 0),         "⚠️", DANGER),
        ]
        self._stat_row(cards_data)

        cards_data2 = [
            ("Total Peminjaman",  pinjam.get('total', 0),       "📋", INFO),
            ("Pending",           pinjam.get('pending', 0),     "⏳", WARNING),
            ("Disetujui",         pinjam.get('disetujui', 0),   "✓",  SUCCESS),
            ("Selesai",           pinjam.get('selesai', 0),     "🏁", PRIMARY),
        ]
        self._stat_row(cards_data2)

        cards_data3 = [
            ("Total Denda",       rupiah(denda.get('total_nominal', 0)),         "💰", WARNING),
            ("Belum Bayar",       rupiah(denda.get('nominal_belum_bayar', 0)),   "❌", DANGER),
            ("Transaksi Denda",   denda.get('total', 0),                          "📊", PRIMARY),
            ("Lunas",             denda.get('lunas', 0),                          "✅", SUCCESS),
        ]
        self._stat_row(cards_data3)

    def _build_peminjam_stats(self):
        from db.peminjaman_db import get_peminjaman
        from db.denda_db import get_denda
        my_p = get_peminjaman(user_id=self.user['id'], role='peminjam')
        actv  = sum(1 for p in my_p if p['status'] == 'disetujui')
        pend  = sum(1 for p in my_p if p['status'] == 'pending')
        selesai = sum(1 for p in my_p if p['status'] == 'selesai')

        from db.denda_db import get_denda
        my_d = get_denda(user_id=self.user['id'], role='peminjam')
        unpaid = sum(1 for d in my_d if d['status'] == 'belum_bayar')
        total_denda = sum(float(d['jumlah']) for d in my_d if d['status'] == 'belum_bayar')

        cards = [
            ("Sedang Dipinjam",  actv,              "🔧", SUCCESS),
            ("Pending",          pend,              "⏳", WARNING),
            ("Selesai",          selesai,           "✅", PRIMARY),
            ("Denda Belum Bayar",rupiah(total_denda),"💰", DANGER),
        ]
        self._stat_row(cards)

    def _stat_row(self, cards_data):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 12))
        for title, val, icon, color in cards_data:
            StatCard(row, title=title, value=val, icon=icon, color=color).pack(
                side="left", fill="both", expand=True, padx=5
            )

    def _build_recent_table(self, role):
        ctk.CTkFrame(self, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=(8, 16))
        SectionHeader(self, title="📋  Peminjaman Terbaru").pack(fill="x", pady=(0, 12))

        cols = ["ID", "Peminjam", "Tgl Pinjam", "Tgl Kembali", "Status", "Alat"]
        widths = [50, 160, 110, 110, 100, 260]
        tbl = DataTable(self, columns=cols, col_widths=widths, height=260)
        tbl.pack(fill="x")

        uid = self.user['id'] if role == 'peminjam' else None
        data = get_peminjaman(user_id=uid, role=role)[:15]
        rows = []
        for p in data:
            rows.append((
                p['id'],
                p.get('nama_peminjam', '-'),
                tgl(p.get('tanggal_pinjam')),
                tgl(p.get('tanggal_kembali')),
                status_label(p.get('status', '')),
                (p.get('daftar_alat') or '-')[:50],
            ))
        tbl.load(rows)
