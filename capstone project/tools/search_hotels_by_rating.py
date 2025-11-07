from langchain.tools import tool
from database.db_connection import get_connection

@tool("search_hotels_by_rating", return_direct=True)
def search_hotels_by_rating(min_rating: float) -> str:
    """Find hotels with rating above given value."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, city, rating FROM hotels WHERE rating >= %s;", (min_rating,))
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    if not hotels:
        return f"No hotels found with rating ≥ {min_rating}."
    return "\n".join([f"{h[0]} ({h[1]}) — ⭐{h[2]}" for h in hotels])
