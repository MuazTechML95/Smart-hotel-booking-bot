from langchain.tools import tool
from database.db_connection import get_connection

@tool("search_hotel_by_name", return_direct=True)
def search_hotel_by_name(hotel_name: str) -> str:
    """Search a hotel by partial or full name."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, city, rating FROM hotels WHERE lower(name) LIKE lower(%s);", (f"%{hotel_name}%",))
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    if not hotels:
        return f"No hotels found matching '{hotel_name}'."
    return "\n".join([f"{h[0]} ({h[1]}) — ⭐{h[2]}" for h in hotels])
