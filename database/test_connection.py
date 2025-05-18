import mysql.connector

try:
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='seqato123',
        database='stocks_db'
    )
    print("✅ Connected to MySQL!")
except mysql.connector.Error as err:
    print("❌ Error:", err)
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("Connection closed.")
