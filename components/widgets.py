import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from config import *


class DataTable(ctk.CTkFrame):
    """Komponen tabel data reusable dengan ttk.Treeview"""

    def __init__(self, parent, columns: list[str], col_widths: list[int] = None, **kwargs):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=12, **kwargs)
        self.columns = columns
        self._setup_style()
        self._build(col_widths)

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
            background=TABLE_BG,
            foreground=TEXT_PRIMARY,
            fieldbackground=TABLE_BG,
            rowheight=38,
            font=(FONT_FAMILY, 11),
            borderwidth=0,
        )
        style.configure("Custom.Treeview.Heading",
            background="#0F172A",
            foreground=TEXT_MUTED,
            font=(FONT_FAMILY, 10, "bold"),
            borderwidth=0,
            relief="flat",
            padding=(8, 10),
        )
        style.map("Custom.Treeview",
            background=[("selected", PRIMARY)],
            foreground=[("selected", "white")],
        )
        style.layout("Custom.Treeview", [
            ('Custom.Treeview.treearea', {'sticky': 'nswe'})
        ])

    def _build(self, col_widths):
        self.tree = ttk.Treeview(
            self, columns=self.columns, show="headings",
            style="Custom.Treeview", selectmode="browse"
        )
        for i, col in enumerate(self.columns):
            w = (col_widths[i] if col_widths and i < len(col_widths) else 130)
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=w, minwidth=60, anchor="w")

        sb = ctk.CTkScrollbar(self, command=self.tree.yview, width=8)
        self.tree.configure(yscrollcommand=sb.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 4))

        # Alternating rows
        self.tree.tag_configure("odd",  background=TABLE_BG)
        self.tree.tag_configure("even", background=TABLE_ROW)

    def load(self, rows: list[tuple]):
        self.tree.delete(*self.tree.get_children())
        for i, row in enumerate(rows):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=row, tags=(tag,))

    def get_selected_id(self, col_index=0):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])['values'][col_index]

    def get_selected_row(self):
        sel = self.tree.selection()
        if not sel:
            return None
        return self.tree.item(sel[0])['values']

    def bind_select(self, callback):
        self.tree.bind("<<TreeviewSelect>>", callback)

    def bind_double(self, callback):
        self.tree.bind("<Double-1>", callback)


class StatCard(ctk.CTkFrame):
    """Card statistik untuk dashboard"""

    def __init__(self, parent, title, value, icon="•", color=PRIMARY, **kwargs):
        super().__init__(parent, fg_color=CARD_BG, corner_radius=14,
                         border_width=1, border_color=CARD_BORDER, **kwargs)
        self._color = color
        self._build(title, value, icon, color)

    def _build(self, title, value, icon, color):
        # Accent bar kiri
        accent = ctk.CTkFrame(self, width=4, fg_color=color, corner_radius=2)
        accent.pack(side="left", fill="y", padx=(10, 0), pady=10)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(side="left", fill="both", expand=True, padx=14, pady=14)

        # Icon
        icon_lbl = ctk.CTkLabel(body, text=icon, font=ctk.CTkFont(size=22), text_color=color)
        icon_lbl.pack(anchor="w")

        self.val_lbl = ctk.CTkLabel(body, text=str(value),
                                     font=ctk.CTkFont(size=30, weight="bold"),
                                     text_color=TEXT_PRIMARY)
        self.val_lbl.pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(body, text=title, font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w")

    def update_value(self, value):
        self.val_lbl.configure(text=str(value))


class SectionHeader(ctk.CTkFrame):
    """Header section dengan judul dan tombol aksi"""

    def __init__(self, parent, title, btn_text=None, btn_cmd=None, btn2_text=None, btn2_cmd=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        if btn2_text and btn2_cmd:
            ctk.CTkButton(self, text=btn2_text, command=btn2_cmd, width=130, height=34,
                          fg_color="#334155", hover_color="#475569",
                          font=ctk.CTkFont(size=12)).pack(side="right", padx=(8, 0))
        if btn_text and btn_cmd:
            ctk.CTkButton(self, text=btn_text, command=btn_cmd, width=130, height=34,
                          fg_color=PRIMARY, hover_color=PRIMARY_HV,
                          font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")


class SearchBar(ctk.CTkFrame):
    """Bar pencarian dengan callback"""

    def __init__(self, parent, placeholder="Cari...", on_search=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.on_search = on_search
        self.entry = ctk.CTkEntry(self, placeholder_text=placeholder,
                                   width=280, height=36,
                                   fg_color=INPUT_BG,
                                   border_color=CARD_BORDER)
        self.entry.pack(side="left")
        self.entry.bind("<Return>", self._fire)
        ctk.CTkButton(self, text="🔍", width=36, height=36,
                      fg_color=PRIMARY, hover_color=PRIMARY_HV,
                      command=self._fire).pack(side="left", padx=(6, 0))

    def _fire(self, *_):
        if self.on_search:
            self.on_search(self.entry.get().strip())

    def get(self):
        return self.entry.get().strip()


class Modal(ctk.CTkToplevel):
    """Base class untuk dialog/popup"""

    def __init__(self, parent, title, width=480, height=400):
        super().__init__(parent)
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.grab_set()
        self.focus()
        self.configure(fg_color=SIDEBAR_BG)
        self.result = None

        ctk.CTkLabel(self, text=title,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(20, 10), padx=24, anchor="w")

        self.body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=24)

        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.pack(fill="x", padx=24, pady=16)

    def add_footer_buttons(self, ok_text="Simpan", ok_cmd=None, cancel_text="Batal"):
        ctk.CTkButton(self.footer, text=cancel_text, width=100, height=36,
                      fg_color="#334155", hover_color="#475569",
                      command=self.destroy).pack(side="right", padx=(8, 0))
        ctk.CTkButton(self.footer, text=ok_text, width=120, height=36,
                      fg_color=PRIMARY, hover_color=PRIMARY_HV,
                      command=ok_cmd or self.destroy).pack(side="right")

    def field(self, label, widget_fn, **kwargs):
        ctk.CTkLabel(self.body, text=label, text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        w = widget_fn(self.body, **kwargs)
        w.pack(fill="x", pady=(0, 4))
        return w

    def error(self, msg):
        if hasattr(self, '_err_lbl'):
            self._err_lbl.configure(text=msg, text_color=DANGER)
        else:
            self._err_lbl = ctk.CTkLabel(self.footer, text=msg, text_color=DANGER,
                                          font=ctk.CTkFont(size=11))
            self._err_lbl.pack(side="left")

    def show_error(self, msg):
        self.error(msg)



class DatePicker(ctk.CTkFrame):
    """Date picker dengan kalender popup"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        from datetime import date
        
        self.selected_date = date.today()
        
        # Entry untuk menampilkan tanggal
        self.entry = ctk.CTkEntry(
            self, 
            height=36,
            fg_color=INPUT_BG,
            border_color=CARD_BORDER,
            font=ctk.CTkFont(size=13)
        )
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.insert(0, str(self.selected_date))
        self.entry.configure(state="readonly")
        
        # Tombol kalender
        self.btn = ctk.CTkButton(
            self,
            text="📅",
            width=36,
            height=36,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HV,
            font=ctk.CTkFont(size=16),
            command=self._show_calendar
        )
        self.btn.pack(side="left", padx=(4, 0))
    
    def _show_calendar(self):
        """Tampilkan popup kalender"""
        from tkcalendar import Calendar
        import tkinter as tk
        
        # Buat popup window
        popup = ctk.CTkToplevel(self)
        popup.title("Pilih Tanggal")
        popup.geometry("300x280")
        popup.resizable(False, False)
        popup.grab_set()
        popup.focus()
        
        # Posisikan di tengah parent
        popup.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() - 300) // 2
        y = self.winfo_rooty() + self.winfo_height() + 5
        popup.geometry(f"+{x}+{y}")
        
        # Frame untuk kalender
        cal_frame = ctk.CTkFrame(popup, fg_color=CARD_BG)
        cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Kalender
        cal = Calendar(
            cal_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            selectbackground=PRIMARY,
            selectforeground="white",
            normalbackground=CARD_BG,
            normalforeground=TEXT_PRIMARY,
            weekendbackground=CARD_BG,
            weekendforeground=WARNING,
            othermonthbackground=INPUT_BG,
            othermonthforeground=TEXT_MUTED,
            headersbackground=PRIMARY,
            headersforeground="white",
            borderwidth=0,
            font=(FONT_FAMILY, 10),
        )
        cal.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Set tanggal saat ini
        if self.selected_date:
            cal.selection_set(self.selected_date)
        
        # Tombol OK dan Cancel
        btn_frame = ctk.CTkFrame(popup, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        def on_ok():
            self.selected_date = cal.selection_get()
            self.entry.configure(state="normal")
            self.entry.delete(0, "end")
            self.entry.insert(0, str(self.selected_date))
            self.entry.configure(state="readonly")
            popup.destroy()
        
        def on_cancel():
            popup.destroy()
        
        ctk.CTkButton(
            btn_frame,
            text="Batal",
            width=80,
            height=32,
            fg_color=CARD_BG,
            hover_color=CARD_BORDER,
            command=on_cancel
        ).pack(side="right", padx=(4, 0))
        
        ctk.CTkButton(
            btn_frame,
            text="OK",
            width=80,
            height=32,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HV,
            command=on_ok
        ).pack(side="right")
    
    def get(self):
        """Ambil tanggal yang dipilih dalam format string YYYY-MM-DD"""
        return str(self.selected_date)
    
    def set(self, date_str):
        """Set tanggal dari string YYYY-MM-DD"""
        from datetime import datetime
        try:
            self.selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            self.entry.configure(state="normal")
            self.entry.delete(0, "end")
            self.entry.insert(0, str(self.selected_date))
            self.entry.configure(state="readonly")
        except:
            pass
