import customtkinter as ctk
from config import *
from db.notifikasi_db import count_unread


class Sidebar(ctk.CTkFrame):
    MENU_ITEMS = [
        ("dashboard",   "🏠", "Dashboard"),
        ("alat",        "🔧", "Alat"),
        ("peminjaman",  "📋", "Peminjaman"),
        ("pengembalian","↩️",  "Pengembalian"),
        ("denda",       "💰", "Denda"),
        ("laporan",     "📊", "Laporan"),
        ("notifikasi",  "🔔", "Notifikasi"),
        ("---", "", ""),
        ("users",       "👥", "Pengguna"),
        ("log",         "📜", "Log Aktivitas"),
    ]

    def __init__(self, parent, user: dict, on_navigate, on_logout):
        super().__init__(parent, fg_color=SIDEBAR_BG, width=220, corner_radius=0)
        self.pack_propagate(False)
        self.user = user
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self._active = None
        self._btns = {}
        self._build()

    def _build(self):
        # Logo
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(24, 8))
        ctk.CTkLabel(logo_frame, text="⚙️", font=ctk.CTkFont(size=28)).pack(side="left")
        ctk.CTkLabel(logo_frame, text=" PeminjamanAlat",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkFrame(self, fg_color=CARD_BORDER, height=1).pack(fill="x", padx=16, pady=8)

        # User info
        user_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10)
        user_frame.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkLabel(user_frame, text=self.user['name'][:22],
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w", padx=12, pady=(10, 2))
        role_color = {"admin": PRIMARY, "petugas": SUCCESS, "peminjam": WARNING}
        rc = role_color.get(self.user['role_name'], TEXT_MUTED)
        ctk.CTkLabel(user_frame, text=f"● {self.user['role_name'].title()}",
                     font=ctk.CTkFont(size=11), text_color=rc).pack(anchor="w", padx=12, pady=(0, 10))

        # Menu scroll
        menu_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color=SIDEBAR_BG)
        menu_scroll.pack(fill="both", expand=True, padx=8)

        role = self.user['role_name']
        for key, icon, label in self.MENU_ITEMS:
            if key == "---":
                if role == 'admin':
                    ctk.CTkFrame(menu_scroll, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=8, padx=4)
                continue
            if key in ("users", "log") and role != 'admin':
                continue
            if key == "laporan" and role not in ('admin', 'petugas'):
                continue
            # Menu pengembalian bisa diakses semua role
            btn = ctk.CTkButton(
                menu_scroll,
                text=f"  {icon}  {label}",
                anchor="w",
                fg_color="transparent",
                hover_color="#1E3A5F",
                text_color=TEXT_MUTED,
                corner_radius=8,
                height=40,
                font=ctk.CTkFont(size=13),
                command=lambda k=key: self._nav(k),
            )
            btn.pack(fill="x", pady=2)
            self._btns[key] = btn

        # Logout
        ctk.CTkFrame(self, fg_color=CARD_BORDER, height=1).pack(fill="x", padx=16, pady=4)
        ctk.CTkButton(self, text="  🚪  Keluar", anchor="w",
                      fg_color="transparent", hover_color="#3B0000",
                      text_color=DANGER, height=40,
                      font=ctk.CTkFont(size=13),
                      command=self.on_logout).pack(fill="x", padx=8, pady=(0, 16))

    def _nav(self, key):
        self.set_active(key)
        self.on_navigate(key)

    def set_active(self, key):
        if self._active and self._active in self._btns:
            self._btns[self._active].configure(fg_color="transparent", text_color=TEXT_MUTED)
        self._active = key
        if key in self._btns:
            self._btns[key].configure(fg_color=PRIMARY, text_color="white")
