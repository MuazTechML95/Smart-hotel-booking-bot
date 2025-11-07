from langchain.tools import tool
from database.db_connection import get_connection
@tool("get_available_rooms", return_direct=True)
def get_available_rooms(hotel_name: str) -> str:
    """Get list of available rooms in a hotel."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT hr.room_number, hr.room_type, hr.price_per_night
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE lower(h.name) LIKE lower(%s)
        AND hr.is_available = TRUE;
    """, (f"%{hotel_name}%",))
    rooms = cur.fetchall()
    cur.close()
    conn.close()
    if not rooms:
        return f"No available rooms in '{hotel_name}'."
    return "\n".join([f"{r[0]} — {r[1]} — ₹{r[2]}" for r in rooms])
