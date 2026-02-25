import customtkinter as ctk
import importlib
from config import *
from utils.auth import logout, is_admin
from components.sidebar import Sidebar
from db.notifikasi_db import count_unread


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, user: dict, on_logout):
        super().__init__(parent, fg_color=CONTENT_BG, corner_radius=0)
        self.pack(fill="both", expand=True)
        self.user = user
        self.on_logout = on_logout
        self._build()
        self._navigate("dashboard")

    def _build(self):
        # Sidebar
        self.sidebar = Sidebar(self, self.user, self._navigate, self._logout)
        self.sidebar.pack(side="left", fill="y")

        # Right area
        self.right = ctk.CTkFrame(self, fg_color=CONTENT_BG, corner_radius=0)
        self.right.pack(side="left", fill="both", expand=True)

        # Topbar
        self.topbar = ctk.CTkFrame(self.right, fg_color=TOPBAR_BG, height=54, corner_radius=0)
        self.topbar.pack(fill="x")
        self.topbar.pack_propagate(False)

        self.page_title = ctk.CTkLabel(self.topbar, text="Dashboard",
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color=TEXT_PRIMARY)
        self.page_title.pack(side="left", padx=20)

        # Theme toggle
        theme_text = "🌙 Dark" if CURRENT_THEME == "light" else "☀️ Light"
        self.theme_btn = ctk.CTkButton(self.topbar, text=theme_text, width=90, height=32,
                                        fg_color=CARD_BG, hover_color=CARD_BORDER,
                                        text_color=TEXT_MUTED,
                                        font=ctk.CTkFont(size=12),
                                        command=self._toggle_theme)
        self.theme_btn.pack(side="right", padx=(0, 8))

        # Notif badge
        self.notif_btn = ctk.CTkButton(self.topbar, text="🔔  0", width=80, height=32,
                                        fg_color=CARD_BG, hover_color=CARD_BORDER,
                                        text_color=TEXT_MUTED,
                                        font=ctk.CTkFont(size=12),
                                        command=lambda: self._navigate("notifikasi"))
        self.notif_btn.pack(side="right", padx=(0, 8))
        self._poll_notif()

        # Content area
        self.content = ctk.CTkFrame(self.right, fg_color=CONTENT_BG, corner_radius=0)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _navigate(self, page: str):
        titles = {
            "dashboard":    "🏠  Dashboard",
            "alat":         "🔧  Manajemen Alat",
            "peminjaman":   "📋  Peminjaman",
            "pengembalian": "↩️   Pengembalian",
            "denda":        "💰  Denda",
            "laporan":      "📊  Laporan",
            "notifikasi":   "🔔  Notifikasi",
            "users":        "👥  Manajemen Pengguna",
            "log":          "📜  Log Aktivitas",
        }
        self.page_title.configure(text=titles.get(page, page.title()))
        self.sidebar.set_active(page)

        for w in self.content.winfo_children():
            w.destroy()

        view_map = {
            "dashboard":    ("views.dashboard_view",    "DashboardView"),
            "alat":         ("views.alat_view",         "AlatView"),
            "peminjaman":   ("views.peminjaman_view",   "PeminjamanView"),
            "pengembalian": ("views.pengembalian_view", "PengembalianView"),
            "denda":        ("views.denda_view",        "DendaView"),
            "laporan":      ("views.laporan_view",      "LaporanView"),
            "notifikasi":   ("views.notifikasi_view",   "NotifikasiView"),
            "users":        ("views.user_view",         "UserView"),
            "log":          ("views.log_view",          "LogView"),
        }
        if page in view_map:
            mod_path, cls_name = view_map[page]
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            cls(self.content, user=self.user).pack(fill="both", expand=True)

    def _logout(self):
        logout()
        self.on_logout()

    def _toggle_theme(self):
        """Toggle antara dark dan light theme"""
        import config
        import tkinter.messagebox as msg
        
        new_theme = "light" if config.CURRENT_THEME == "dark" else "dark"
        config.save_theme(new_theme)
        
        # Show message
        result = msg.askyesno("Theme Changed", 
                              f"Tema akan diubah ke {new_theme.upper()} mode.\n\n"
                              "Aplikasi perlu direstart untuk menerapkan perubahan.\n\n"
                              "Restart sekarang?")
        
        if result:
            # Restart aplikasi
            import sys
            import os
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def _poll_notif(self):
        try:
            n = count_unread(self.user['id'])
            if n > 0:
                self.notif_btn.configure(text=f"🔔  {n}", text_color=WARNING)
            else:
                self.notif_btn.configure(text="🔔  0", text_color=TEXT_MUTED)
        except Exception:
            pass
        self.after(30_000, self._poll_notif)
