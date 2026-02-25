import customtkinter as ctk
import os
import json
from config import *
from utils.auth import login, current_user


class LoginView(ctk.CTkFrame):
    REMEMBER_FILE = ".remember_me.json"
    
    def __init__(self, parent, on_success):
        super().__init__(parent, fg_color=CONTENT_BG)
        self.pack(fill="both", expand=True)
        self.on_success = on_success
        self._build()
        self._load_remembered()

    def _build(self):
        # Background gradient effect (left panel)
        left = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=420, corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Left panel content
        ctk.CTkFrame(left, fg_color="transparent").pack(expand=True)
        brand = ctk.CTkFrame(left, fg_color="transparent")
        brand.pack(pady=40, padx=40)
        ctk.CTkLabel(brand, text="⚙️", font=ctk.CTkFont(size=64)).pack()
        ctk.CTkLabel(brand, text="Peminjaman Alat",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(8, 4))
        ctk.CTkLabel(brand, text="Sistem Manajemen Peminjaman\nPeralatan Modern",
                     font=ctk.CTkFont(size=13),
                     text_color=TEXT_MUTED, justify="center").pack()

        ctk.CTkFrame(left, fg_color="transparent").pack(expand=True)
        ctk.CTkLabel(left, text="© 2026 Peminjaman Alat",
                     text_color=TEXT_MUTED, font=ctk.CTkFont(size=10)).pack(pady=16)

        # Right panel (form)
        right = ctk.CTkFrame(self, fg_color=CONTENT_BG, corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form_outer = ctk.CTkFrame(right, fg_color="transparent")
        form_outer.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form_outer, text="Selamat Datang 👋",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(form_outer, text="Masuk ke akun Anda untuk melanjutkan",
                     font=ctk.CTkFont(size=13),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(4, 32))

        form = ctk.CTkFrame(form_outer, fg_color=CARD_BG, corner_radius=16,
                             border_width=1, border_color=CARD_BORDER, width=400, height=450)
        form.pack()
        form.pack_propagate(False)

        inner = ctk.CTkFrame(form, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=32)

        # Email dengan autocomplete
        ctk.CTkLabel(inner, text="Email", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        self.email = ctk.CTkEntry(inner, placeholder_text="admin@example.com",
                                   height=42, fg_color=INPUT_BG,
                                   border_color=CARD_BORDER,
                                   font=ctk.CTkFont(size=13))
        self.email.pack(fill="x", pady=(4, 4))
        self.email.bind("<KeyRelease>", self._on_email_type)
        
        # Autocomplete suggestions
        self.suggestions_frame = ctk.CTkFrame(inner, fg_color=CARD_BG, 
                                              corner_radius=8, height=0)
        self.suggestions_frame.pack(fill="x", pady=(0, 12))
        self.suggestions_frame.pack_forget()  # Hide initially

        # Password
        ctk.CTkLabel(inner, text="Password", text_color=TEXT_LABEL,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
        
        # Password frame dengan toggle button
        pass_frame = ctk.CTkFrame(inner, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(4, 8))
        
        self.passwd = ctk.CTkEntry(pass_frame, placeholder_text="••••••••",
                                    show="•", height=42, fg_color=INPUT_BG,
                                    border_color=CARD_BORDER,
                                    font=ctk.CTkFont(size=13))
        self.passwd.pack(side="left", fill="x", expand=True)
        self.passwd.bind("<Return>", lambda _: self._do_login())
        
        # Toggle show/hide password button
        self.show_pass_btn = ctk.CTkButton(pass_frame, text="👁", width=42, height=42,
                                           fg_color=INPUT_BG, hover_color=CARD_BORDER,
                                           border_color=CARD_BORDER, border_width=1,
                                           font=ctk.CTkFont(size=16),
                                           command=self._toggle_password)
        self.show_pass_btn.pack(side="left", padx=(8, 0))
        self.password_visible = False

        # Error
        self.err = ctk.CTkLabel(inner, text="", text_color=DANGER,
                                 font=ctk.CTkFont(size=11))
        self.err.pack(pady=(0, 8))
        
        # Remember Me checkbox
        self.remember_var = ctk.BooleanVar(value=True)
        remember_frame = ctk.CTkFrame(inner, fg_color="transparent")
        remember_frame.pack(fill="x", pady=(0, 8))
        self.remember_check = ctk.CTkCheckBox(
            remember_frame,
            text="Ingat saya",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
            fg_color=PRIMARY,
            hover_color=PRIMARY_HV,
            border_color=CARD_BORDER
        )
        self.remember_check.pack(side="left")

        # Login button
        self.btn = ctk.CTkButton(inner, text="Masuk →", height=44,
                                  fg_color=PRIMARY, hover_color=PRIMARY_HV,
                                  font=ctk.CTkFont(size=14, weight="bold"),
                                  command=self._do_login, corner_radius=10)
        self.btn.pack(fill="x")

        # Hint
        ctk.CTkLabel(inner, text="Default: admin@example.com / password",
                     text_color=TEXT_MUTED, font=ctk.CTkFont(size=10)).pack(pady=(12, 0))

    def _toggle_password(self):
        """Toggle show/hide password"""
        if self.password_visible:
            self.passwd.configure(show="•")
            self.show_pass_btn.configure(text="👁")
            self.password_visible = False
        else:
            self.passwd.configure(show="")
            self.show_pass_btn.configure(text="🙈")
            self.password_visible = True
    
    def _load_remembered(self):
        """Load email yang tersimpan jika ada"""
        try:
            if os.path.exists(self.REMEMBER_FILE):
                with open(self.REMEMBER_FILE, 'r') as f:
                    data = json.load(f)
                    if data.get('email'):
                        self.email.delete(0, "end")
                        self.email.insert(0, data['email'])
                        self.passwd.focus()  # Focus ke password
        except Exception:
            pass
    
    def _on_email_type(self, event):
        """Tampilkan suggestions saat user mengetik email"""
        text = self.email.get().strip().lower()
        
        # Email suggestions
        suggestions = [
            "admin@example.com",
            "petugas@example.com", 
            "peminjam@example.com"
        ]
        
        # Filter suggestions
        if len(text) >= 2:
            matches = [s for s in suggestions if text in s.lower()]
            if matches:
                self._show_suggestions(matches)
                return
        
        # Hide suggestions jika tidak ada match
        self.suggestions_frame.pack_forget()
    
    def _show_suggestions(self, suggestions):
        """Tampilkan suggestion list"""
        # Clear previous suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Show frame
        self.suggestions_frame.pack(fill="x", pady=(0, 12))
        
        # Add suggestions
        for email in suggestions[:3]:  # Max 3 suggestions
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=email,
                height=32,
                fg_color="transparent",
                hover_color=PRIMARY,
                text_color=TEXT_PRIMARY,
                anchor="w",
                font=ctk.CTkFont(size=12),
                command=lambda e=email: self._select_suggestion(e)
            )
            btn.pack(fill="x", padx=8, pady=2)
    
    def _select_suggestion(self, email):
        """Pilih email dari suggestion"""
        self.email.delete(0, "end")
        self.email.insert(0, email)
        self.suggestions_frame.pack_forget()
        self.passwd.focus()
    
    def _save_remember(self, email):
        """Simpan email jika remember me dicentang"""
        try:
            if self.remember_var.get():
                with open(self.REMEMBER_FILE, 'w') as f:
                    json.dump({'email': email}, f)
            else:
                # Hapus file jika tidak dicentang
                if os.path.exists(self.REMEMBER_FILE):
                    os.remove(self.REMEMBER_FILE)
        except Exception:
            pass
    
    def _do_login(self):
        email = self.email.get().strip()
        pw    = self.passwd.get()
        if not email or not pw:
            self.err.configure(text="⚠  Email dan password wajib diisi")
            return
        self.btn.configure(state="disabled", text="Memuat...")
        self.update()
        ok, result = login(email, pw)
        if ok:
            self._save_remember(email)  # Simpan email jika berhasil
            self.on_success(result)
        else:
            self.err.configure(text=f"⚠  {result}")
            self.btn.configure(state="normal", text="Masuk →")
