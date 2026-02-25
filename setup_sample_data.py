#!/usr/bin/env python3
"""
Script untuk insert sample data ke database
Jalankan setelah migration/schema sudah dibuat
"""

import bcrypt
from db.connection import Database


def hash_password(password: str) -> str:
    """Hash password dengan bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def insert_roles():
    """Insert roles default"""
    print("📝 Inserting roles...")
    cursor = Database.cursor()
    
    roles = [
        (1, 'admin'),
        (2, 'petugas'),
        (3, 'peminjam'),
    ]
    
    for role_id, name in roles:
        cursor.execute("""
            INSERT IGNORE INTO roles (id, name, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
        """, (role_id, name))
    
    Database.commit()
    print("✓ Roles inserted")


def insert_users():
    """Insert users default"""
    print("📝 Inserting users...")
    cursor = Database.cursor()
    
    # Password default: "password"
    hashed = hash_password('password')
    
    users = [
        ('Administrator', 'admin@example.com', hashed, 1),
        ('Petugas Satu', 'petugas@example.com', hashed, 2),
        ('John Peminjam', 'peminjam@example.com', hashed, 3),
        ('Jane Doe', 'jane@example.com', hashed, 3),
        ('Bob Smith', 'bob@example.com', hashed, 3),
    ]
    
    for name, email, password, role_id in users:
        cursor.execute("""
            INSERT IGNORE INTO users (name, email, password, role_id, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, 1, NOW(), NOW())
        """, (name, email, password, role_id))
    
    Database.commit()
    print("✓ Users inserted")


def insert_kategori():
    """Insert kategori alat"""
    print("📝 Inserting kategori...")
    cursor = Database.cursor()
    
    kategori = [
        ('Alat Listrik', 'Alat-alat yang menggunakan listrik'),
        ('Alat Ukur', 'Alat untuk mengukur dimensi dan besaran'),
        ('Alat Pertukangan', 'Alat untuk pekerjaan pertukangan/bangunan'),
        ('Alat Keselamatan', 'APD dan alat keselamatan kerja'),
        ('Alat Elektronik', 'Peralatan elektronik dan komponen'),
    ]
    
    for nama, deskripsi in kategori:
        cursor.execute("""
            INSERT IGNORE INTO kategori (nama, deskripsi, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
        """, (nama, deskripsi))
    
    Database.commit()
    print("✓ Kategori inserted")


def insert_alat():
    """Insert alat sample"""
    print("📝 Inserting alat...")
    cursor = Database.cursor()
    
    # Get kategori IDs
    cursor.execute("SELECT id, nama FROM kategori")
    kategori_map = {row['nama']: row['id'] for row in cursor.fetchall()}
    
    alat = [
        (kategori_map['Alat Listrik'], 'Bor Listrik', 'BOR-001', 'Bor listrik 500 watt', 5),
        (kategori_map['Alat Listrik'], 'Gerinda Tangan', 'GRD-001', 'Gerinda sudut 4 inch', 3),
        (kategori_map['Alat Listrik'], 'Las Listrik', 'LAS-001', 'Mesin las SMAW 200A', 2),
        (kategori_map['Alat Listrik'], 'Mesin Potong', 'POT-001', 'Mesin potong besi', 2),
        
        (kategori_map['Alat Ukur'], 'Meteran 5m', 'MTR-001', 'Meteran baja panjang 5 meter', 10),
        (kategori_map['Alat Ukur'], 'Multimeter', 'MLT-001', 'Multimeter digital auto-range', 4),
        (kategori_map['Alat Ukur'], 'Jangka Sorong', 'JNG-001', 'Jangka sorong digital', 6),
        (kategori_map['Alat Ukur'], 'Waterpass', 'WTR-001', 'Waterpass 60cm', 5),
        
        (kategori_map['Alat Pertukangan'], 'Palu', 'PLU-001', 'Palu besi 1 kg', 8),
        (kategori_map['Alat Pertukangan'], 'Obeng Set', 'OBG-001', 'Set obeng + dan - berbagai ukuran', 6),
        (kategori_map['Alat Pertukangan'], 'Tang Set', 'TNG-001', 'Set tang kombinasi', 5),
        (kategori_map['Alat Pertukangan'], 'Gergaji', 'GRG-001', 'Gergaji tangan', 4),
        
        (kategori_map['Alat Keselamatan'], 'Helm Safety', 'HLM-001', 'Helm proyek SNI', 10),
        (kategori_map['Alat Keselamatan'], 'Sarung Tangan', 'STG-001', 'Sarung tangan kulit las', 15),
        (kategori_map['Alat Keselamatan'], 'Kacamata Safety', 'KCM-001', 'Kacamata pelindung UV', 12),
        (kategori_map['Alat Keselamatan'], 'Sepatu Safety', 'SPT-001', 'Sepatu safety steel toe', 8),
        
        (kategori_map['Alat Elektronik'], 'Solder', 'SLD-001', 'Solder listrik 40W', 7),
        (kategori_map['Alat Elektronik'], 'Oscilloscope', 'OSC-001', 'Oscilloscope digital 2 channel', 2),
        (kategori_map['Alat Elektronik'], 'Power Supply', 'PWR-001', 'Power supply DC 0-30V', 3),
    ]
    
    for kategori_id, nama, kode, deskripsi, stok in alat:
        cursor.execute("""
            INSERT IGNORE INTO alat (kategori_id, nama, kode, deskripsi, stok, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, 'tersedia', NOW(), NOW())
        """, (kategori_id, nama, kode, deskripsi, stok))
    
    Database.commit()
    print("✓ Alat inserted")


def main():
    print("\n" + "=" * 60)
    print("  SETUP SAMPLE DATA - Aplikasi Peminjaman Alat")
    print("=" * 60 + "\n")
    
    try:
        # Test koneksi
        Database.get_connection()
        print("✓ Database connection OK\n")
        
        # Insert data
        insert_roles()
        insert_users()
        insert_kategori()
        insert_alat()
        
        print("\n" + "=" * 60)
        print("✓ Sample data berhasil diinsert!")
        print("=" * 60)
        print("\n📋 Akun yang tersedia:")
        print("   • admin@example.com / password (Admin)")
        print("   • petugas@example.com / password (Petugas)")
        print("   • peminjam@example.com / password (Peminjam)")
        print("   • jane@example.com / password (Peminjam)")
        print("   • bob@example.com / password (Peminjam)")
        print("\n🚀 Aplikasi siap digunakan!")
        print("   Jalankan: python main.py\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("Pastikan:")
        print("  1. MySQL sudah berjalan")
        print("  2. Database sudah dibuat")
        print("  3. Schema/migration sudah dijalankan")
        print("  4. Konfigurasi di config.py sudah benar\n")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
