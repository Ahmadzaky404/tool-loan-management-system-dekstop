import customtkinter as ctk
import tkinter.messagebox as msg
from config import *
from components.widgets import DataTable, SectionHeader, Modal
from db.denda_db import get_denda, bayar_denda
from utils.auth import is_peminjam
from utils.format import tgl, rupiah, status_label


class DendaView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._data = []
        self._build()
        self.refresh()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        SectionHeader(header, "Data Denda").pack(side="left")

        # Filter
        fbar = ctk.CTkFrame(self, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(fbar, text="Status:", text_color=TEXT_MUTED).pack(side="left", padx=(0, 4))
        self.status_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(fbar, values=["Semua", "belum_bayar", "lunas"],
                          variable=self.status_var,
                          command=lambda _: self.refresh(),
                          fg_color=CARD_BG, button_color=PRIMARY, width=140).pack(side="left")

        cols   = ["ID", "Peminjam", "Jumlah Denda", "Status", "Metode", "Tgl Bayar", "Keterangan"]
        widths = [50, 160, 130, 110, 100, 110, 220]
        self.tbl = DataTable(self, cols, widths)
        self.tbl.pack(fill="both", expand=True)

        abar = ctk.CTkFrame(self, fg_color="transparent")
        abar.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(abar, text="💳  Bayar Denda", width=140, height=36,
                      fg_color=SUCCESS, hover_color="#166534",
                      command=self._bayar).pack(side="left")
        ctk.CTkButton(abar, text="🔄  Refresh", width=100, height=36,
                      fg_color=CARD_BG, hover_color=CARD_BORDER,
                      command=self.refresh).pack(side="left", padx=(8, 0))

    def refresh(self):
        st = self.status_var.get() if hasattr(self, 'status_var') else ''
        if st == "Semua":
            st = ''
        uid  = self.user['id'] if is_peminjam() else None
        role = self.user['role_name']
        self._data = get_denda(user_id=uid, role=role, status=st)
        rows = [(
            d['id'], d.get('nama_peminjam', '-'),
            rupiah(d.get('jumlah', 0)),
            status_label(d.get('status', '')),
            d.get('metode_pembayaran') or '-',
            tgl(d.get('tanggal_bayar')),
            (d.get('keterangan') or '-')[:40],
        ) for d in self._data]
        self.tbl.load(rows)

    def _get_selected(self):
        row = self.tbl.get_selected_row()
        if not row:
            msg.showwarning("Pilih Data", "Pilih data denda terlebih dahulu")
            return None
        return next((d for d in self._data if d['id'] == row[0]), None)

    def _bayar(self):
        d = self._get_selected()
        if not d:
            return
        if d['status'] == 'lunas':
            msg.showinfo("Info", "Denda ini sudah lunas")
            return
        BayarDendaModal(self, denda=d, on_done=self.refresh)


class BayarDendaModal(Modal):
    def __init__(self, parent, denda: dict, on_done=None):
        super().__init__(parent, f"Bayar Denda #{denda['id']}", width=440, height=340)
        self.denda   = denda
        self.on_done = on_done
        self._build_form()
        self.add_footer_buttons("💳  Konfirmasi Bayar", self._submit)

    def _build_form(self):
        ctk.CTkLabel(self.body, text=f"Peminjam: {self.denda.get('nama_peminjam', '-')}",
                     text_color=TEXT_PRIMARY).pack(anchor="w", pady=(8, 4))
        ctk.CTkLabel(self.body, text=f"Total Denda: {rupiah(self.denda.get('jumlah', 0))}",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=DANGER).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(self.body, text=f"Keterangan: {self.denda.get('keterangan') or '-'}",
                     text_color=TEXT_MUTED, font=ctk.CTkFont(size=11), wraplength=380).pack(anchor="w", pady=(0, 12))

        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=8)
        ctk.CTkLabel(self.body, text="Metode Pembayaran *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        self.metode_var = ctk.StringVar(value="tunai")
        ctk.CTkOptionMenu(self.body, values=["tunai", "transfer"],
                          variable=self.metode_var,
                          fg_color=INPUT_BG, button_color=PRIMARY).pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body, text="Bukti / Keterangan", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        self.e_bukti = ctk.CTkEntry(self.body, placeholder_text="No. transfer / nama teller / dll",
                                     height=36, fg_color=INPUT_BG, border_color=CARD_BORDER)
        self.e_bukti.pack(fill="x")

    def _submit(self):
        metode = self.metode_var.get()
        bukti  = self.e_bukti.get().strip()
        if msg.askyesno("Konfirmasi", f"Konfirmasi pembayaran denda {rupiah(self.denda['jumlah'])} via {metode}?"):
            ok = bayar_denda(self.denda['id'], metode, bukti)
            if ok:
                msg.showinfo("Berhasil", "Pembayaran denda berhasil dikonfirmasi!")
                self.destroy()
                if self.on_done:
                    self.on_done()
            else:
                self.show_error("Gagal memperbarui data denda")
