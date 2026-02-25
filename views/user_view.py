import customtkinter as ctk
import tkinter.messagebox as msg
from config import *
from components.widgets import DataTable, SectionHeader, SearchBar, Modal
from db.user_db import get_all_users, get_all_roles, insert_user, update_user, toggle_user_status, delete_user


class UserView(ctk.CTkFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        self.user = user
        self._data = []
        self._build()
        self.refresh()

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))
        SectionHeader(header, "Manajemen Pengguna",
                      btn_text="+ Tambah User", btn_cmd=self._add).pack(side="left", fill="x", expand=True)

        fbar = ctk.CTkFrame(self, fg_color="transparent")
        fbar.pack(fill="x", pady=(0, 12))
        self.search = SearchBar(fbar, "Cari nama / email...", on_search=lambda q: self.refresh(search=q))
        self.search.pack(side="left")

        cols   = ["ID", "Nama", "Email", "Role", "Status"]
        widths = [50, 200, 240, 100, 90]
        self.tbl = DataTable(self, cols, widths)
        self.tbl.pack(fill="both", expand=True)

        abar = ctk.CTkFrame(self, fg_color="transparent")
        abar.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(abar, text="✏️  Edit", width=100, height=34,
                      fg_color=WARNING, hover_color="#B45309",
                      command=self._edit).pack(side="left", padx=(0, 8))
        ctk.CTkButton(abar, text="🔄  Toggle Aktif", width=130, height=34,
                      fg_color=INFO, hover_color="#0E7490",
                      command=self._toggle).pack(side="left", padx=(0, 8))
        ctk.CTkButton(abar, text="🗑  Hapus", width=100, height=34,
                      fg_color=DANGER, hover_color="#991B1B",
                      command=self._delete).pack(side="left")

    def refresh(self, search=''):
        self._data = get_all_users(search=search)
        rows = [(
            d['id'], d['name'], d['email'],
            d.get('role_name', '-').title(),
            "Aktif" if d.get('is_active') else "Nonaktif",
        ) for d in self._data]
        self.tbl.load(rows)

    def _get_selected(self):
        row = self.tbl.get_selected_row()
        if not row:
            msg.showwarning("Pilih User", "Pilih pengguna terlebih dahulu")
            return None
        return next((d for d in self._data if d['id'] == row[0]), None)

    def _add(self):
        UserFormModal(self, title="Tambah Pengguna", on_save=self.refresh)

    def _edit(self):
        u = self._get_selected()
        if u:
            UserFormModal(self, title="Edit Pengguna", user=u, on_save=self.refresh)

    def _toggle(self):
        u = self._get_selected()
        if u:
            status = "nonaktifkan" if u['is_active'] else "aktifkan"
            if msg.askyesno("Konfirmasi", f"Yakin {status} akun {u['name']}?"):
                toggle_user_status(u['id'])
                self.refresh()

    def _delete(self):
        u = self._get_selected()
        if u:
            if u['id'] == self.user['id']:
                msg.showerror("Tidak Bisa", "Tidak bisa menghapus akun sendiri")
                return
            if msg.askyesno("Hapus", f"Hapus pengguna '{u['name']}'?"):
                try:
                    delete_user(u['id'])
                    self.refresh()
                except Exception as e:
                    msg.showerror("Gagal", str(e))


class UserFormModal(Modal):
    def __init__(self, parent, title, user=None, on_save=None):
        super().__init__(parent, title, width=480, height=420)
        self.u       = user
        self.on_save = on_save
        self._roles  = get_all_roles()
        self._build_form()
        self.add_footer_buttons("Simpan", self._save)

    def _build_form(self):
        for lbl, attr, show in [("Nama *", "name", ""), ("Email *", "email", ""), ("Password" + (" (kosong = tidak diganti)" if self.u else " *"), "password", "•")]:
            ctk.CTkLabel(self.body, text=lbl, text_color=TEXT_LABEL, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
            e = ctk.CTkEntry(self.body, height=38, fg_color=INPUT_BG, border_color=CARD_BORDER,
                              show=show if show else "")
            if self.u and attr != 'password':
                e.insert(0, str(self.u.get(attr, '')))
            e.pack(fill="x", pady=(0, 4))
            setattr(self, f"e_{attr}", e)

        ctk.CTkLabel(self.body, text="Role *", text_color=TEXT_LABEL, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))
        role_names = [r['name'] for r in self._roles]
        cur_role = self.u.get('role_name', role_names[0]) if self.u else role_names[0]
        self.role_var = ctk.StringVar(value=cur_role)
        ctk.CTkOptionMenu(self.body, values=role_names, variable=self.role_var,
                          fg_color=INPUT_BG, button_color=PRIMARY).pack(fill="x", pady=(0, 4))

    def _save(self):
        nama  = self.e_name.get().strip()
        email = self.e_email.get().strip()
        pw    = self.e_password.get()
        role  = next((r for r in self._roles if r['name'] == self.role_var.get()), None)

        if not nama or not email:
            self.show_error("Nama & email wajib diisi")
            return
        if not self.u and not pw:
            self.show_error("Password wajib diisi untuk user baru")
            return
        if not role:
            self.show_error("Pilih role yang valid")
            return

        data = {'name': nama, 'email': email, 'password': pw, 'role_id': role['id']}
        try:
            if self.u:
                update_user(self.u['id'], data)
            else:
                insert_user(data)
            self.destroy()
            if self.on_save:
                self.on_save()
        except Exception as e:
            self.show_error(str(e)[:80])
