import customtkinter as ctk
from config import *
from db.connection import Database
from views.login_view import LoginView
from views.main_window import MainWindow


# Set appearance mode berdasarkan CURRENT_THEME
ctk.set_appearance_mode("dark" if CURRENT_THEME == "dark" else "light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(WINDOW_SIZE)
        self.minsize(*MIN_SIZE)
        
        # Test koneksi database
        try:
            Database.get_connection()
            print("✓ Koneksi database berhasil")
        except Exception as e:
            import tkinter.messagebox as msg
            msg.showerror("Koneksi Gagal", 
                         f"Tidak dapat terhubung ke database:\n\n{e}\n\n"
                         f"Pastikan MySQL sudah berjalan dan konfigurasi di config.py sudah benar.")
            self.destroy()
            return
        
        self.show_login()
    
    def show_login(self):
        """Tampilkan halaman login"""
        for widget in self.winfo_children():
            widget.destroy()
        LoginView(self, on_success=self.show_main)
    
    def show_main(self, user):
        """Tampilkan main window setelah login berhasil"""
        for widget in self.winfo_children():
            widget.destroy()
        MainWindow(self, user=user, on_logout=self.show_login)
    
    def on_closing(self):
        """Cleanup saat aplikasi ditutup"""
        try:
            Database.close()
        except:
            pass
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
