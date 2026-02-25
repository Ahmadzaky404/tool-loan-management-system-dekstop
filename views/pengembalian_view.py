import customtkinter as ctk
import tkinter.messagebox as msg
from datetime import date
from config import *
from components.widgets import DataTable, SectionHeader, Modal, DatePicker
from db.pengembalian_db import (get_pengembalian, get_detail_pengembalian,
                                 insert_pengembalian, verifikasi_pengembalian)
from db.peminjaman_db import get_peminjaman_disetujui_tanpa_kembali, get_detail_peminjaman
from utils.auth import is_admin_or_petugas, is_peminjam
from utils.format import tgl, status_label, rupiah


class PengembalianView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._data = []
        self._build()
        self.refresh()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        SectionHeader(
            header, "Data Pengembalian",
            btn_text="+ Ajukan Pengembalian" if is_peminjam() else None,
            btn_cmd=self._buat if is_peminjam() else None,
        ).pack(side="left", fill="x", expand=True)

        cols = ["ID", "Peminjam", "Tgl Kembali Aktual", "Tgl Kembali Rencana", "Kondisi", "Verifikator"]
        widths = [50, 160, 150, 160, 90, 150]
        self.tbl = DataTable(self, cols, widths)
        self.tbl.pack(fill="both", expand=True)

        abar = ctk.CTkFrame(self, fg_color="transparent")
        abar.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(abar, text="🔍  Detail", width=110, height=34,
                      fg_color=INFO, hover_color="#0E7490",
                      command=self._detail).pack(side="left", padx=(0, 8))
        if is_admin_or_petugas():
            ctk.CTkButton(abar, text="✅  Verifikasi", width=130, height=34,
                          fg_color=SUCCESS, hover_color="#166534",
                          command=self._verifikasi).pack(side="left")

    def refresh(self):
        uid  = self.user['id'] if is_peminjam() else None
        role = self.user['role_name']
        self._data = get_pengembalian(user_id=uid, role=role)
        rows = [(
            d['id'],
            d.get('nama_peminjam', '-'),
            tgl(d.get('tanggal_kembali_aktual')),
            tgl(d.get('tanggal_kembali')),
            status_label(d.get('kondisi_alat', '')),
            d.get('nama_verifikator') or 'Belum diverifikasi',
        ) for d in self._data]
        self.tbl.load(rows)

    def _get_selected(self):
        row = self.tbl.get_selected_row()
        if not row:
            msg.showwarning("Pilih Data", "Pilih data pengembalian terlebih dahulu")
            return None
        return next((d for d in self._data if d['id'] == row[0]), None)

    def _buat(self):
        BuatPengembalianModal(self, user=self.user, on_save=self.refresh)

    def _detail(self):
        d = self._get_selected()
        if d:
            DetailPengembalianModal(self, data=d)

    def _verifikasi(self):
        d = self._get_selected()
        if not d:
            return
        if d.get('nama_verifikator'):
            msg.showwarning("Sudah Diverifikasi", "Pengembalian ini sudah diverifikasi")
            return
        VerifikasiModal(self, data=d, user_id=self.user['id'], on_done=self.refresh)


class BuatPengembalianModal(Modal):
    def __init__(self, parent, user, on_save=None):
        super().__init__(parent, "Ajukan Pengembalian", width=700, height=550)
        self.user    = user
        self.on_save = on_save
        self._peminjaman_list = get_peminjaman_disetujui_tanpa_kembali(
            user_id=user['id'], role=user['role_name']
        )
        self._kondisi = {}
        self._details = []
        self._selected_id = None
        self._build_form()
        self.add_footer_buttons("Ajukan Pengembalian", self._submit)

    def _build_form(self):
        ctk.CTkLabel(self.body, text="Pilih Peminjaman *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        opts = [f"#{p['id']} — Tgl kembali: {tgl(p.get('tanggal_kembali'))} — {p.get('nama_peminjam','')}"
                for p in self._peminjaman_list]
        self.pinjam_var = ctk.StringVar(value=opts[0] if opts else "Tidak ada peminjaman aktif")
        ctk.CTkOptionMenu(self.body, values=opts or ["Tidak ada peminjaman aktif"],
                          variable=self.pinjam_var, fg_color=INPUT_BG,
                          button_color=PRIMARY,
                          command=self._on_pinjam_select).pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body, text="Tanggal Kembali Aktual *", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        self.e_tgl = DatePicker(self.body)
        self.e_tgl.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(self.body, text="Catatan", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        self.e_catatan = ctk.CTkEntry(self.body, height=36, fg_color=INPUT_BG, border_color=CARD_BORDER)
        self.e_catatan.pack(fill="x", pady=(0, 8))

        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=8)
        ctk.CTkLabel(self.body, text="Kondisi Alat per Item:", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")

        self.kondisi_container = ctk.CTkFrame(self.body, fg_color="transparent")
        self.kondisi_container.pack(fill="x", pady=(0, 8))
        
        # Load kondisi alat setelah semua widget dibuat
        if opts:
            self._on_pinjam_select(opts[0])

    def _on_pinjam_select(self, val):
        try:
            pid = int(val.split("#")[1].split(" ")[0])
        except Exception:
            return
        self._selected_id = pid
        self._details = get_detail_peminjaman(pid)
        self._kondisi = {}
        self._e_kondisi = {}
        for w in self.kondisi_container.winfo_children():
            w.destroy()
        for d in self._details:
            aid  = d['alat_id']
            nama = d['alat_nama']
            jml  = d['jumlah']
            self._kondisi[aid] = {'baik': jml, 'rusak': 0, 'hilang': 0}
            row = ctk.CTkFrame(self.kondisi_container, fg_color=INPUT_BG, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"[{d['kode']}] {nama} (total: {jml})",
                          text_color=TEXT_PRIMARY, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
            cols = ctk.CTkFrame(row, fg_color="transparent")
            cols.pack(fill="x", padx=10, pady=(0, 6))
            self._e_kondisi[aid] = {}
            for lbl, key, default in [("Baik", "baik", jml), ("Rusak", "rusak", 0), ("Hilang", "hilang", 0)]:
                ctk.CTkLabel(cols, text=f"{lbl}:", text_color=TEXT_MUTED, width=42).pack(side="left")
                e = ctk.CTkEntry(cols, width=52, height=28, fg_color=CONTENT_BG, border_color=CARD_BORDER)
                e.insert(0, str(default))
                e.pack(side="left", padx=(0, 12))
                self._e_kondisi[aid][key] = e

    def _submit(self):
        if not self._selected_id:
            self.show_error("Pilih peminjaman")
            return
        tgl_aktual = self.e_tgl.get().strip()
        if not tgl_aktual:
            self.show_error("Tanggal wajib diisi")
            return
        kondisi = {}
        for aid, fields in self._e_kondisi.items():
            try:
                kondisi[aid] = {k: int(e.get() or 0) for k, e in fields.items()}
            except ValueError:
                self.show_error("Jumlah kondisi harus angka")
                return
        ok, result = insert_pengembalian(self._selected_id, tgl_aktual, kondisi, self.e_catatan.get())
        if ok:
            msg.showinfo("Berhasil", f"Pengembalian #{result} berhasil diajukan!")
            self.destroy()
            if self.on_save:
                self.on_save()
        else:
            self.show_error(str(result)[:100])


class DetailPengembalianModal(Modal):
    def __init__(self, parent, data: dict):
        super().__init__(parent, f"Detail Pengembalian #{data['id']}", width=540, height=460)
        details = get_detail_pengembalian(data['id'])
        for lbl, val in [
            ("Peminjam",        data.get('nama_peminjam', '-')),
            ("Tgl Pinjam",      tgl(data.get('tanggal_pinjam'))),
            ("Tgl Kembali Rencana", tgl(data.get('tanggal_kembali'))),
            ("Tgl Kembali Aktual",  tgl(data.get('tanggal_kembali_aktual'))),
            ("Kondisi",         status_label(data.get('kondisi_alat', ''))),
            ("Verifikator",     data.get('nama_verifikator') or 'Belum'),
        ]:
            row = ctk.CTkFrame(self.body, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{lbl}:", width=170, anchor="w",
                          text_color=TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row, text=val, anchor="w",
                          text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=8)
        ctk.CTkLabel(self.body, text="Detail Kondisi Alat:", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        for d in details:
            ctk.CTkLabel(self.body,
                          text=f"  • {d['alat_nama']}  — Baik: {d['jumlah_baik']}  Rusak: {d['jumlah_rusak']}  Hilang: {d['jumlah_hilang']}",
                          text_color=TEXT_PRIMARY, anchor="w").pack(anchor="w", pady=2)
        ctk.CTkButton(self.footer, text="Tutup", command=self.destroy,
                      fg_color=CARD_BG, hover_color=CARD_BORDER).pack(side="right")


class VerifikasiModal(Modal):
    def __init__(self, parent, data: dict, user_id, on_done=None):
        super().__init__(parent, f"Verifikasi Pengembalian #{data['id']}", width=600, height=500)
        self.pen_id  = data['id']
        self.user_id = user_id
        self.on_done = on_done
        self.data = data
        self._details = get_detail_pengembalian(data['id'])
        self._denda_entries = {}
        self._build_content()
        self.add_footer_buttons("✅  Verifikasi Sekarang", self._submit)

    def _build_content(self):
        for lbl, val in [
            ("Peminjam",           self.data.get('nama_peminjam', '-')),
            ("Tgl Kembali Aktual", tgl(self.data.get('tanggal_kembali_aktual'))),
            ("Tgl Kembali Rencana",tgl(self.data.get('tanggal_kembali'))),
        ]:
            row = ctk.CTkFrame(self.body, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=f"{lbl}:", width=180, anchor="w",
                          text_color=TEXT_MUTED).pack(side="left")
            ctk.CTkLabel(row, text=val, text_color=TEXT_PRIMARY).pack(side="left")

        ctk.CTkFrame(self.body, fg_color=CARD_BORDER, height=1).pack(fill="x", pady=10)
        
        # Info denda keterlambatan
        try:
            tgl_janji  = self.data.get('tanggal_kembali')
            tgl_aktual = self.data.get('tanggal_kembali_aktual')
            
            if tgl_janji and tgl_aktual:
                if isinstance(tgl_janji, str):
                    from datetime import datetime
                    tgl_janji = datetime.strptime(tgl_janji, '%Y-%m-%d').date()
                if isinstance(tgl_aktual, str):
                    from datetime import datetime
                    tgl_aktual = datetime.strptime(tgl_aktual, '%Y-%m-%d').date()
                
                if tgl_aktual > tgl_janji:
                    hari = (tgl_aktual - tgl_janji).days
                    d_telat = hari * TARIF_KETERLAMBATAN
                    ctk.CTkLabel(self.body, 
                                 text=f"⚠️ Keterlambatan {hari} hari = {rupiah(d_telat)} (otomatis)",
                                 text_color=WARNING, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", pady=(0, 8))
        except Exception as e:
            print(f"Error calculating late fee: {e}")
        
        # Input denda manual untuk barang rusak/hilang
        try:
            has_damage = False
            for d in self._details:
                if d.get('jumlah_rusak', 0) > 0 or d.get('jumlah_hilang', 0) > 0:
                    has_damage = True
                    break
            
            if has_damage:
                ctk.CTkLabel(self.body, text="Input Denda Manual (Opsional):", 
                             text_color=TEXT_LABEL,
                             font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(8, 4))
                ctk.CTkLabel(self.body, 
                             text="Kosongkan untuk menggunakan tarif default",
                             text_color=TEXT_MUTED, font=ctk.CTkFont(size=10)).pack(anchor="w", pady=(0, 8))
                
                for d in self._details:
                    rusak = d.get('jumlah_rusak', 0)
                    hilang = d.get('jumlah_hilang', 0)
                    
                    if rusak > 0 or hilang > 0:
                        card = ctk.CTkFrame(self.body, fg_color=INPUT_BG, corner_radius=8)
                        card.pack(fill="x", pady=4)
                        
                        ctk.CTkLabel(card, text=f"[{d.get('kode', '-')}] {d.get('alat_nama', '-')}",
                                      text_color=TEXT_PRIMARY, 
                                      font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=(8, 4))
                        
                        alat_id = d.get('alat_id')
                        if alat_id:
                            self._denda_entries[alat_id] = {}
                            
                            if rusak > 0:
                                row = ctk.CTkFrame(card, fg_color="transparent")
                                row.pack(fill="x", padx=10, pady=2)
                                ctk.CTkLabel(row, text=f"Rusak ({rusak}x):", 
                                              text_color=TEXT_MUTED, width=120, anchor="w").pack(side="left")
                                e_rusak = ctk.CTkEntry(row, width=150, height=28, 
                                                        fg_color=CONTENT_BG, border_color=CARD_BORDER,
                                                        placeholder_text=f"Default: {rupiah(rusak * TARIF_RUSAK)}")
                                e_rusak.pack(side="left", padx=(4, 0))
                                self._denda_entries[alat_id]['rusak'] = e_rusak
                            
                            if hilang > 0:
                                row = ctk.CTkFrame(card, fg_color="transparent")
                                row.pack(fill="x", padx=10, pady=2)
                                ctk.CTkLabel(row, text=f"Hilang ({hilang}x):", 
                                              text_color=TEXT_MUTED, width=120, anchor="w").pack(side="left")
                                e_hilang = ctk.CTkEntry(row, width=150, height=28, 
                                                         fg_color=CONTENT_BG, border_color=CARD_BORDER,
                                                         placeholder_text=f"Default: {rupiah(hilang * TARIF_HILANG)}")
                                e_hilang.pack(side="left", padx=(4, 0))
                                self._denda_entries[alat_id]['hilang'] = e_hilang
                            
                            ctk.CTkLabel(card, text="", height=4).pack()  # spacing
            else:
                ctk.CTkLabel(self.body, text="✅ Semua alat dalam kondisi baik",
                             text_color=SUCCESS, font=ctk.CTkFont(size=11)).pack(anchor="w")
        except Exception as e:
            print(f"Error building damage input: {e}")
            ctk.CTkLabel(self.body, text="Error memuat data kondisi alat",
                         text_color=DANGER, font=ctk.CTkFont(size=11)).pack(anchor="w")

    def _submit(self):
        # Kumpulkan denda manual
        denda_manual = {}
        for alat_id, entries in self._denda_entries.items():
            denda_manual[alat_id] = {}
            if 'rusak' in entries:
                val = entries['rusak'].get().strip()
                if val:
                    try:
                        denda_manual[alat_id]['rusak'] = float(val.replace(',', '').replace('.', ''))
                    except ValueError:
                        self.show_error("Denda rusak harus berupa angka")
                        return
            if 'hilang' in entries:
                val = entries['hilang'].get().strip()
                if val:
                    try:
                        denda_manual[alat_id]['hilang'] = float(val.replace(',', '').replace('.', ''))
                    except ValueError:
                        self.show_error("Denda hilang harus berupa angka")
                        return
        
        ok, result = verifikasi_pengembalian(self.pen_id, self.user_id, denda_manual if denda_manual else None)
        if ok:
            denda = result
            if denda > 0:
                msg.showinfo("Berhasil", f"Pengembalian diverifikasi.\nTotal denda: {rupiah(denda)}")
            else:
                msg.showinfo("Berhasil", "Pengembalian diverifikasi. Tidak ada denda.")
            self.destroy()
            if self.on_done:
                self.on_done()
        else:
            self.show_error(str(result)[:100])
