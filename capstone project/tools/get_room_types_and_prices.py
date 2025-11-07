from langchain.tools import tool
from database.db_connection import get_connection

@tool("get_room_types_and_prices", return_direct=True)
def get_room_types_and_prices(hotel_name: str) -> str:
    """List room types and prices for a hotel."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT room_type, price_per_night
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE lower(h.name) LIKE lower(%s);
    """, (f"%{hotel_name}%",))
    data = cur.fetchall()
    cur.close()
    conn.close()
    if not data:
        return f"No rooms found for '{hotel_name}'."
    return "\n".join([f"{r[0]} — ₹{r[1]}" for r in data])
