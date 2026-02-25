import customtkinter as ctk
from config import *
from db.notifikasi_db import get_notifikasi, tandai_dibaca, tandai_semua_dibaca
from utils.format import status_color


class NotifikasiView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._build()
        self.refresh()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(header, text="Notifikasi",
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkButton(header, text="✓  Tandai Semua Dibaca", width=180, height=34,
                      fg_color=CARD_BG, hover_color=CARD_BORDER,
                      command=self._baca_semua).pack(side="right", padx=(0, 8))
        ctk.CTkButton(header, text="🔄", width=40, height=34,
                      fg_color=CARD_BG, hover_color=CARD_BORDER,
                      command=self.refresh).pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                              scrollbar_button_color=CARD_BG)
        self.scroll.pack(fill="both", expand=True)

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        notifs = get_notifikasi(self.user['id'])
        if not notifs:
            ctk.CTkLabel(self.scroll, text="Tidak ada notifikasi 🔕",
                          text_color=TEXT_MUTED, font=ctk.CTkFont(size=14)).pack(pady=40)
            return

        type_colors = {
            'info':    INFO,
            'success': SUCCESS,
            'warning': WARNING,
            'error':   DANGER,
        }

        for n in notifs:
            is_read = bool(n.get('is_read'))
            bg = CARD_BG if is_read else "#1E3A5F"
            brd = CARD_BORDER if is_read else PRIMARY

            card = ctk.CTkFrame(self.scroll, fg_color=bg, corner_radius=10,
                                border_width=1, border_color=brd)
            card.pack(fill="x", pady=4, padx=2)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=12, pady=10)

            # Left accent
            color = type_colors.get(n.get('type', 'info'), INFO)
            ctk.CTkFrame(card, fg_color=color, width=4, corner_radius=2).pack(side="left", fill="y", padx=(0, 0))

            # Header row
            hrow = ctk.CTkFrame(inner, fg_color="transparent")
            hrow.pack(fill="x")
            ctk.CTkLabel(hrow, text=n.get('title', '-'),
                          font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=TEXT_PRIMARY).pack(side="left")

            if not is_read:
                ctk.CTkLabel(hrow, text="● Baru", text_color=color,
                              font=ctk.CTkFont(size=11)).pack(side="left", padx=8)

            nid = n['id']
            if not is_read:
                ctk.CTkButton(hrow, text="Tandai dibaca", width=100, height=24,
                              fg_color="transparent", border_width=1, border_color=PRIMARY,
                              text_color=PRIMARY, hover_color=CARD_BG,
                              font=ctk.CTkFont(size=10),
                              command=lambda i=nid: self._baca_satu(i)).pack(side="right")

            ctk.CTkLabel(inner, text=n.get('message', ''),
                          text_color=TEXT_MUTED, font=ctk.CTkFont(size=12),
                          anchor="w", wraplength=700, justify="left").pack(fill="x", pady=(4, 0))

            # Timestamp
            ts = n.get('created_at')
            ts_str = str(ts)[:16] if ts else ''
            ctk.CTkLabel(inner, text=ts_str, text_color="#64748B",
                          font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(4, 0))

    def _baca_satu(self, nid):
        tandai_dibaca(nid)
        self.refresh()

    def _baca_semua(self):
        tandai_semua_dibaca(self.user['id'])
        self.refresh()
