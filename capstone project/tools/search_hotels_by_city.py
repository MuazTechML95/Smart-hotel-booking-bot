from langchain.tools import tool
from database.db_connection import get_connection

@tool("search_hotels_by_city", return_direct=True)
def search_hotels_by_city(city: str) -> str:
    """Search hotels by city name."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, rating FROM hotels WHERE lower(city) = lower(%s);", (city,))
    hotels = cur.fetchall()
    cur.close()
    conn.close()
    if not hotels:
        return f"No hotels found in {city}."
    return "\n".join([f"{h[1]} — ⭐{h[2]}" for h in hotels])
