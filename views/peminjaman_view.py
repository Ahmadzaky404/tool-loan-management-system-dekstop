import customtkinter as ctk
import tkinter.messagebox as msg
from datetime import date
from config import *
from components.widgets import DataTable, SectionHeader, SearchBar, Modal, DatePicker
from db.peminjaman_db import (get_peminjaman, get_peminjaman_by_id,
                               get_detail_peminjaman, insert_peminjaman,
                               approve_peminjaman, reject_peminjaman)
from db.alat_db import get_alat_tersedia
from utils.auth import is_admin_or_petugas, is_peminjam
from utils.format import tgl, status_label, rupiah


class PeminjamanView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._data = []
        self._build()
        self.refresh()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        can_buat = is_peminjam()
        SectionHeader(
            header, "Data Peminjaman",
            btn_text="+ Buat Peminjaman" if can_buat else None,
            btn_cmd=self._buat if can_buat else None,
        ).pack(side="left", fill="x", expand=True)

        # Filter
        fbar = ctk.CTkFrame(self, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12))
        self.search = SearchBar(fbar, "Cari peminjam...", on_search=lambda q: self.refresh(search=q))
        self.search.pack(side="left")

        ctk.CTkLabel(fbar, text="Status:", text_color=TEXT_MUTED).pack(side="left", padx=(16, 4))
        self.status_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(fbar, values=["Semua", "pending", "disetujui", "ditolak", "selesai"],
                          variable=self.status_var, command=lambda _: self.refresh(),
                          fg_color=CARD_BG, button_color=PRIMARY, width=130).pack(side="left")

        cols = ["ID", "Peminjam", "Tgl Pinjam", "Tgl Kembali", "Status", "Alat"]
        widths = [50, 160, 110, 110, 100, 280]
        self.tbl = DataTable(self, cols, widths)
        self.tbl.pack(fill="both", expand=True)
        self.tbl.bind_double(self._detail)

        # Action bar (admin/petugas)
        abar = ctk.CTkFrame(self, fg_color="transparent")
        abar.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(abar, text="🔍  Detail", width=110, height=34,
                      fg_color=INFO, hover_color="#0E7490",
                      command=self._detail).pack(side="left", padx=(0, 8))
        if is_admin_or_petugas():
            ctk.CTkButton(abar, text="✅  Setujui", width=110, height=34,
                          fg_color=SUCCESS, hover_color="#166534",
                          command=self._approve).pack(side="left", padx=(0, 8))
            ctk.CTkButton(abar, text="❌  Tolak", width=110, height=34,
                          fg_color=DANGER, hover_color="#991B1B",
                          command=self._reject).pack(side="left")

    def refresh(self, search=''):
        st = self.status_var.get() if hasattr(self, 'status_var') else ''
        if st == "Semua":
            st = ''
        uid  = self.user['id'] if is_peminjam() else None
        role = self.user['role_name']
        self._data = get_peminjaman(user_id=uid, role=role, status=st, search=search)
        rows = [(
            p['id'], p.get('nama_peminjam', '-'),
            tgl(p.get('tanggal_pinjam')), tgl(p.get('tanggal_kembali')),
            status_label(p.get('status', '')),
            (p.get('daftar_alat') or '-')[:55],
        ) for p in self._data]
        self.tbl.load(rows)

    def _get_selected(self):
        row = self.tbl.get_selected_row()
        if not row:
            msg.showwarning("Pilih Data", "Pilih peminjaman terlebih dahulu")
            return None
        return next((p for p in self._data if p['id'] == row[0]), None)

    def _buat(self):
        BuatPeminjamanModal(self, user=self.user, on_save=self.refresh)

    def _detail(self, *_):
        p = self._get_selected()
        if p:
            DetailPeminjamanModal(self, peminjaman=p)

    def _approve(self):
        p = self._get_selected()
        if not p:
            return
        if p['status'] != 'pending':
            msg.showwarning("Tidak Bisa", "Hanya bisa menyetujui peminjaman berstatus Pending")
            return
        if msg.askyesno("Konfirmasi", f"Setujui peminjaman #{p['id']} dari {p['nama_peminjam']}?"):
            ok, pesan = approve_peminjaman(p['id'], self.user['id'])
            if ok:
                msg.showinfo("Berhasil", pesan)
                self.refresh()
            else:
                msg.showerror("Gagal", pesan)

    def _reject(self):
        p = self._get_selected()
        if not p:
            return
        if p['status'] != 'pending':
            msg.showwarning("Tidak Bisa", "Hanya bisa menolak peminjaman berstatus Pending")
            return
        RejectModal(self, pid=p['id'], nama=p['nama_peminjam'],
                    user_id=self.user['id'], on_done=self.refresh)


class BuatPeminjamanModal(Modal):
    def __init__(self, parent, user, on_save=None):
        super().__init__(parent, "Buat Peminjaman Baru", width=700, height=680)
        self.user    = user
        self.on_save = on_save
        self._items  = []   # [{alat_id, jumlah, nama}]
        self._alat_list = get_alat_tersedia()
        self._build_form()
        self.add_footer_buttons("Ajukan Peminjaman", self._submit)

    def _build_form(self):
        row1 = ctk.CTkFrame(self.body, fg_color="transparent")
        row1.pack(fill="x", pady=(8, 0))

        # Tanggal Pinjam dengan DatePicker
        col1 = ctk.CTkFrame(row1, fg_color="transparent")
        col1.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        ctk.CTkLabel(col1, text="Tgl Pinjam *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.e_tgl_pinjam = DatePicker(col1)
        self.e_tgl_pinjam.pack(fill="x", pady=(4, 0))

        # Tanggal Kembali dengan DatePicker
        col2 = ctk.CTkFrame(row1, fg_color="transparent")
        col2.grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(col2, text="Tgl Kembali *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.e_tgl_kembali = DatePicker(col2)
        self.e_tgl_kembali.pack(fill="x", pady=(4, 0))
        
        row1.columnconfigure([0, 1], weight=1)

        # Pilih alat
        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=12)
        ctk.CTkLabel(self.body, text="Pilih Alat", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        pick = ctk.CTkFrame(self.body, fg_color="transparent")
        pick.pack(fill="x", pady=(6, 0))

        alat_names = [f"{a['kode']} - {a['nama']} (stok:{a['stok']})" for a in self._alat_list]
        self.alat_var = ctk.StringVar(value=alat_names[0] if alat_names else "Tidak ada alat")
        ctk.CTkOptionMenu(pick, values=alat_names or ["Tidak ada alat"],
                          variable=self.alat_var, fg_color=INPUT_BG,
                          button_color=PRIMARY, width=350).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(pick, text="Jml:", text_color=TEXT_MUTED).pack(side="left")
        self.e_jml = ctk.CTkEntry(pick, width=60, height=34, fg_color=INPUT_BG,
                                   border_color=CARD_BORDER)
        self.e_jml.insert(0, "1")
        self.e_jml.pack(side="left", padx=(4, 8))
        ctk.CTkButton(pick, text="＋ Tambah", width=100, height=34,
                      fg_color=SUCCESS, hover_color="#166534",
                      command=self._add_item).pack(side="left")

        # Daftar item
        ctk.CTkLabel(self.body, text="Daftar Alat Dipinjam:", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(12, 4))
        self.item_frame = ctk.CTkFrame(self.body, fg_color=INPUT_BG, corner_radius=8)
        self.item_frame.pack(fill="x")
        self.item_lbl = ctk.CTkLabel(self.item_frame, text="(belum ada alat dipilih)",
                                      text_color=TEXT_MUTED, font=ctk.CTkFont(size=11))
        self.item_lbl.pack(pady=8)

    def _add_item(self):
        val = self.alat_var.get()
        kode = val.split(" - ")[0]
        alat = next((a for a in self._alat_list if a['kode'] == kode), None)
        if not alat:
            return
        try:
            jml = int(self.e_jml.get())
        except ValueError:
            self.show_error("Jumlah harus angka")
            return
        if jml <= 0 or jml > alat['stok']:
            self.show_error(f"Jumlah harus 1 - {alat['stok']}")
            return
        existing = next((i for i in self._items if i['alat_id'] == alat['id']), None)
        if existing:
            existing['jumlah'] += jml
        else:
            self._items.append({'alat_id': alat['id'], 'jumlah': jml, 'nama': alat['nama']})
        self._refresh_items()

    def _refresh_items(self):
        for w in self.item_frame.winfo_children():
            w.destroy()
        if not self._items:
            ctk.CTkLabel(self.item_frame, text="(belum ada alat dipilih)",
                          text_color=TEXT_MUTED).pack(pady=8)
            return
        for item in self._items:
            row = ctk.CTkFrame(self.item_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(row, text=f"• {item['nama']}  ×  {item['jumlah']}",
                          text_color=TEXT_PRIMARY).pack(side="left")
            ctk.CTkButton(row, text="✕", width=28, height=24, fg_color=DANGER,
                          hover_color="#7F1D1D",
                          command=lambda it=item: self._remove_item(it)).pack(side="right")

    def _remove_item(self, item):
        self._items = [i for i in self._items if i['alat_id'] != item['alat_id']]
        self._refresh_items()

    def _submit(self):
        tgl_p = self.e_tgl_pinjam.get().strip()
        tgl_k = self.e_tgl_kembali.get().strip()
        if not tgl_p or not tgl_k:
            self.show_error("Tanggal wajib diisi")
            return
        if not self._items:
            self.show_error("Pilih minimal 1 alat")
            return

        ok, result = insert_peminjaman(self.user['id'], tgl_p, tgl_k, self._items)
        if ok:
            msg.showinfo("Berhasil", f"Peminjaman #{result} berhasil diajukan!")
            self.destroy()
            if self.on_save:
                self.on_save()
        else:
            self.show_error(str(result)[:100])


class DetailPeminjamanModal(Modal):
    def __init__(self, parent, peminjaman: dict):
        super().__init__(parent, f"Detail Peminjaman #{peminjaman['id']}", width=560, height=480)
        p = peminjaman
        details = get_detail_peminjaman(p['id'])
        labels = [
            ("Peminjam",       p.get('nama_peminjam', '-')),
            ("Tanggal Pinjam", tgl(p.get('tanggal_pinjam'))),
            ("Tgl Kembali",    tgl(p.get('tanggal_kembali'))),
            ("Status",         status_label(p.get('status', ''))),
            ("Disetujui Oleh", p.get('nama_approver') or '-'),
            ("Alasan Tolak",   p.get('alasan_penolakan') or '-'),
        ]
        for lbl, val in labels:
            row = ctk.CTkFrame(self.body, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{lbl}:", width=140, anchor="w",
                          text_color=TEXT_MUTED, font=ctk.CTkFont(size=12)).pack(side="left")
            ctk.CTkLabel(row, text=val, anchor="w",
                          text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=12)).pack(side="left")

        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=10)
        ctk.CTkLabel(self.body, text="Detail Alat:", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

        for d in details:
            ctk.CTkLabel(self.body, text=f"  • [{d['kode']}] {d['alat_nama']}  ×  {d['jumlah']}",
                          text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w", pady=2)

        ctk.CTkButton(self.footer, text="Tutup", command=self.destroy,
                      fg_color=CARD_BG, hover_color=CARD_BORDER).pack(side="right")


class RejectModal(Modal):
    def __init__(self, parent, pid, nama, user_id, on_done=None):
        super().__init__(parent, f"Tolak Peminjaman #{pid}", width=440, height=280)
        self.pid = pid
        self.user_id = user_id
        self.on_done = on_done
        ctk.CTkLabel(self.body, text=f"Peminjam: {nama}", text_color=TEXT_PRIMARY).pack(anchor="w", pady=(8, 12))
        ctk.CTkLabel(self.body, text="Alasan Penolakan *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.e_alasan = ctk.CTkTextbox(self.body, height=80, fg_color=INPUT_BG)
        self.e_alasan.pack(fill="x", pady=(4, 0))
        self.add_footer_buttons("Tolak Peminjaman", self._submit)

    def _submit(self):
        alasan = self.e_alasan.get("1.0", "end").strip()
        if not alasan:
            self.show_error("Alasan wajib diisi")
            return
        ok, pesan = reject_peminjaman(self.pid, alasan, self.user_id)
        if ok:
            msg.showinfo("Berhasil", pesan)
            self.destroy()
            if self.on_done:
                self.on_done()
        else:
            self.show_error(pesan[:80])
