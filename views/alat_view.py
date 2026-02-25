import customtkinter as ctk
import tkinter.messagebox as msg
from config import *
from components.widgets import DataTable, SectionHeader, SearchBar, Modal
from db.alat_db import (get_all_alat, get_all_kategori, insert_alat,
                         update_alat, delete_alat)
from utils.auth import is_admin
from utils.format import status_label, status_color


class AlatView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._admin = is_admin()
        self._data  = []
        self._build()
        self.refresh()

    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        SectionHeader(
            header, "Manajemen Alat",
            btn_text="+ Tambah Alat" if self._admin else None,
            btn_cmd=self._add if self._admin else None,
        ).pack(side="left", fill="x", expand=True)

        # Filter bar
        fbar = ctk.CTkFrame(self, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12))
        self.search = SearchBar(fbar, "Cari nama / kode...", on_search=self._search)
        self.search.pack(side="left")

        ctk.CTkLabel(fbar, text="Status:", text_color=TEXT_MUTED).pack(side="left", padx=(16, 4))
        self.status_var = ctk.StringVar(value="Semua")
        ctk.CTkOptionMenu(fbar, values=["Semua", "tersedia", "dipinjam", "rusak"],
                          variable=self.status_var,
                          command=lambda _: self.refresh(),
                          fg_color=CARD_BG, button_color=PRIMARY,
                          width=130).pack(side="left")

        # Table
        cols   = ["ID", "Kode", "Nama Alat", "Kategori", "Stok", "Status", "Deskripsi"]
        widths = [50, 90, 200, 140, 60, 100, 200]
        self.tbl = DataTable(self, cols, widths)
        self.tbl.pack(fill="both", expand=True)

        # Action bar
        if self._admin:
            abar = ctk.CTkFrame(self, fg_color="transparent")
            abar.pack(fill="x", pady=(10, 0))
            ctk.CTkButton(abar, text="✏️  Edit", width=110, height=34,
                          fg_color=WARNING, hover_color="#B45309",
                          command=self._edit).pack(side="left", padx=(0, 8))
            ctk.CTkButton(abar, text="🗑  Hapus", width=110, height=34,
                          fg_color=DANGER, hover_color="#991B1B",
                          command=self._delete).pack(side="left")

    def refresh(self, search=''):
        st = self.status_var.get() if hasattr(self, 'status_var') else ''
        if st == "Semua":
            st = ''
        self._data = get_all_alat(search=search, status=st)
        rows = [(
            d['id'], d['kode'], d['nama'], d['kategori_nama'],
            d['stok'], status_label(d['status']), (d.get('deskripsi') or '')[:40]
        ) for d in self._data]
        self.tbl.load(rows)

    def _search(self, q):
        self.refresh(search=q)

    def _get_selected(self):
        row = self.tbl.get_selected_row()
        if not row:
            msg.showwarning("Pilih Alat", "Pilih alat terlebih dahulu")
            return None
        aid = row[0]
        return next((d for d in self._data if d['id'] == aid), None)

    def _add(self):
        AlatFormModal(self, title="Tambah Alat", on_save=self.refresh)

    def _edit(self):
        alat = self._get_selected()
        if alat:
            AlatFormModal(self, title="Edit Alat", alat=alat, on_save=self.refresh)

    def _delete(self):
        alat = self._get_selected()
        if alat and msg.askyesno("Hapus", f"Hapus alat '{alat['nama']}'?"):
            try:
                delete_alat(alat['id'])
                self.refresh()
            except Exception as e:
                msg.showerror("Gagal", str(e))


class AlatFormModal(Modal):
    def __init__(self, parent, title, alat=None, on_save=None):
        super().__init__(parent, title, width=520, height=490)
        self.alat    = alat
        self.on_save = on_save
        self._kategori = get_all_kategori()
        self._build_form()
        self.add_footer_buttons("Simpan", self._save)

    def _build_form(self):
        # Kategori
        ctk.CTkLabel(self.body, text="Kategori *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        kat_names = [k['nama'] for k in self._kategori]
        self.kat_var = ctk.StringVar(value=self.alat['kategori_nama'] if self.alat else (kat_names[0] if kat_names else ''))
        ctk.CTkOptionMenu(self.body, values=kat_names or ["(Belum ada kategori)"],
                          variable=self.kat_var, fg_color=INPUT_BG,
                          button_color=PRIMARY).pack(fill="x", pady=(0, 8))

        for lbl, attr in [("Nama Alat *", "nama"), ("Kode Alat *", "kode"), ("Stok *", "stok")]:
            ctk.CTkLabel(self.body, text=lbl, text_color=TEXT_LABEL,
                         font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            e = ctk.CTkEntry(self.body, height=38, fg_color=INPUT_BG, border_color=CARD_BORDER)
            if self.alat:
                e.insert(0, str(self.alat.get(attr, '')))
            e.pack(fill="x", pady=(0, 4))
            setattr(self, f"e_{attr}", e)

        ctk.CTkLabel(self.body, text="Deskripsi", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        self.e_desc = ctk.CTkTextbox(self.body, height=70, fg_color=INPUT_BG)
        if self.alat and self.alat.get('deskripsi'):
            self.e_desc.insert("1.0", self.alat['deskripsi'])
        self.e_desc.pack(fill="x")

    def _save(self):
        kat_name = self.kat_var.get()
        kat = next((k for k in self._kategori if k['nama'] == kat_name), None)
        if not kat:
            self.show_error("Pilih kategori yang valid")
            return

        nama  = self.e_nama.get().strip()
        kode  = self.e_kode.get().strip()
        stok  = self.e_stok.get().strip()
        desc  = self.e_desc.get("1.0", "end").strip()

        if not nama or not kode or not stok:
            self.show_error("Nama, kode & stok wajib diisi")
            return
        try:
            stok = int(stok)
        except ValueError:
            self.show_error("Stok harus angka")
            return

        data = {'kategori_id': kat['id'], 'nama': nama, 'kode': kode,
                'stok': stok, 'deskripsi': desc}
        try:
            if self.alat:
                update_alat(self.alat['id'], data)
            else:
                insert_alat(data)
            self.destroy()
            if self.on_save:
                self.on_save()
        except Exception as e:
            self.show_error(str(e)[:80])
