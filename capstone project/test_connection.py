# # test_connection.py

# from database.db_connection import get_connection

# try:
#     conn = get_connection()
#     with conn.cursor() as cur:
#         cur.execute("SELECT COUNT(*) FROM hotels;")
#         print("✅ Database connected successfully!")
#         print("Total hotels in database:", cur.fetchone()[0])
#     conn.close()
# except Exception as e:
#     print("❌ Connection failed:", e)
from database.db_connection import get_connection

try:
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM hotels;")
        rows = cur.fetchall()
        print("✅ Database connected successfully!")
        print("Total hotels in database:", len(rows))
        print("\n🏨 Hotel Records:\n")
        for row in rows:
            print(row)

    conn.close()
except Exception as e:
    print("❌ Connection failed:", e)

