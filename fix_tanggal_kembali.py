"""
Script untuk memperbaiki data tanggal_kembali yang NULL
Jalankan script ini jika ada error terkait tanggal_kembali NULL
"""
from db.connection import Database
from datetime import datetime, timedelta

def fix_tanggal_kembali():
    conn = Database.get_connection()
    cur = Database.cursor()
    
    try:
        # Cek data yang tanggal_kembali nya NULL
        cur.execute("""
            SELECT id, user_id, tanggal_pinjam, tanggal_kembali, status
            FROM peminjaman
            WHERE tanggal_kembali IS NULL
        """)
        null_data = cur.fetchall()
        
        if not null_data:
            print("✅ Tidak ada data dengan tanggal_kembali NULL")
            return
        
        print(f"⚠️ Ditemukan {len(null_data)} data dengan tanggal_kembali NULL:")
        for d in null_data:
            print(f"  - ID: {d['id']}, User: {d['user_id']}, Tgl Pinjam: {d['tanggal_pinjam']}, Status: {d['status']}")
        
        # Update tanggal_kembali yang NULL dengan tanggal_pinjam + 7 hari
        cur.execute("""
            UPDATE peminjaman
            SET tanggal_kembali = DATE_ADD(tanggal_pinjam, INTERVAL 7 DAY)
            WHERE tanggal_kembali IS NULL
        """)
        conn.commit()
        
        print(f"\n✅ Berhasil memperbaiki {cur.rowcount} data")
        
        # Verifikasi
        cur.execute("""
            SELECT id, user_id, tanggal_pinjam, tanggal_kembali, status
            FROM peminjaman
            WHERE tanggal_kembali IS NULL
        """)
        remaining = cur.fetchall()
        
        if remaining:
            print(f"\n⚠️ Masih ada {len(remaining)} data yang NULL, akan diset ke hari ini")
            cur.execute("""
                UPDATE peminjaman
                SET tanggal_kembali = CURDATE()
                WHERE tanggal_kembali IS NULL
            """)
            conn.commit()
            print(f"✅ Berhasil memperbaiki {cur.rowcount} data lagi")
        else:
            print("\n✅ Semua data sudah diperbaiki!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Script Perbaikan Tanggal Kembali")
    print("=" * 50)
    fix_tanggal_kembali()
    print("=" * 50)
    input("\nTekan Enter untuk keluar...")
