import customtkinter as ctk
from config import *
from components.widgets import SectionHeader, DataTable
from db.connection import Database
from utils.format import tgl_waktu


class LogView(ctk.CTkScrollableFrame):
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent", scrollbar_button_color=CARD_BG)
        self.user = user
        self._build()
    
    def _build(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        
        SectionHeader(header, title="📜  Log Aktivitas Sistem").pack(side="left")
        
        # Filter
        filter_frame = ctk.CTkFrame(header, fg_color=CARD_BG, corner_radius=10)
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Filter User:", 
                    text_color=TEXT_LABEL, font=ctk.CTkFont(size=11)).pack(side="left", padx=(12, 4))
        
        self.user_filter = ctk.CTkComboBox(
            filter_frame, 
            values=["Semua"] + self._get_users(),
            width=180,
            height=32,
            fg_color=INPUT_BG,
            button_color=PRIMARY,
            command=lambda _: self._load_logs()
        )
        self.user_filter.set("Semua")
        self.user_filter.pack(side="left", padx=(0, 8))
        
        ctk.CTkButton(
            filter_frame,
            text="🔄",
            width=32,
            height=32,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HV,
            command=self._load_logs
        ).pack(side="left", padx=(0, 8))
        
        # Table
        cols = ["ID", "User", "Aktivitas", "Deskripsi", "IP Address", "Waktu"]
        widths = [50, 140, 160, 320, 120, 140]
        self.table = DataTable(self, columns=cols, col_widths=widths, height=500)
        self.table.pack(fill="both", expand=True)
        
        self._load_logs()
    
    def _get_users(self):
        """Ambil daftar user untuk filter"""
        try:
            cur = Database.cursor()
            cur.execute("SELECT name FROM users ORDER BY name")
            return [row['name'] for row in cur.fetchall()]
        except:
            return []
    
    def _load_logs(self):
        """Load data log aktivitas"""
        try:
            cur = Database.cursor()
            
            # Build query
            sql = """
                SELECT l.id, u.name AS user_name, l.aktivitas, l.deskripsi,
                       l.ip_address, l.created_at
                FROM log_aktivitas l
                JOIN users u ON u.id = l.user_id
            """
            params = []
            
            # Filter by user
            selected_user = self.user_filter.get()
            if selected_user != "Semua":
                sql += " WHERE u.name = %s"
                params.append(selected_user)
            
            sql += " ORDER BY l.created_at DESC LIMIT 500"
            
            cur.execute(sql, params)
            logs = cur.fetchall()
            
            # Format data untuk table
            rows = []
            for log in logs:
                rows.append((
                    log['id'],
                    log['user_name'][:20],
                    log['aktivitas'][:25],
                    (log['deskripsi'] or '-')[:50],
                    log['ip_address'] or '-',
                    tgl_waktu(log['created_at'])
                ))
            
            self.table.load(rows)
            
        except Exception as e:
            print(f"Error loading logs: {e}")
