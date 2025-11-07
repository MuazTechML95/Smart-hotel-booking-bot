from langchain.tools import tool
from database.db_connection import get_connection

@tool("get_hotel_details", return_direct=True)
def get_hotel_details(hotel_name: str) -> str:
    """Get details of a hotel."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, city, rating, address, contact FROM hotels WHERE lower(name) LIKE lower(%s);", (f"%{hotel_name}%",))
    h = cur.fetchone()
    cur.close()
    conn.close()
    if not h:
        return f"No details found for '{hotel_name}'."
    return f"{h[0]} ({h[1]})\n⭐ Rating: {h[2]}\n📍 Address: {h[3]}\n📞 Contact: {h[4]}"
