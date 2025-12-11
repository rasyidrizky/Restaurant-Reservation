import psycopg2
try:
    conn = psycopg2.connect(
        dbname="restoran_db",
        user="user",
        password="password",
        host="localhost",
        port="5432"
    )
    print("KONEKSI SUKSES!")
    conn.close()
except Exception as e:
    print(f"KONEKSI GAGAL: {e}")