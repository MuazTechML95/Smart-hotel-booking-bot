from langchain.tools import tool
from database.db_connection import get_connection
from datetime import datetime

def parse_date(s: str):
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()

@tool("check_room_availability_by_dates", return_direct=True)
def check_room_availability_by_dates(room_id: int, check_in: str, check_out: str) -> str:
    """Check if a specific room is available between two dates."""
    ci = parse_date(check_in)
    co = parse_date(check_out)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT check_in, check_out FROM bookings
        WHERE room_id = %s AND status = 'confirmed';
    """, (room_id,))
    bookings = cur.fetchall()
    cur.close()
    conn.close()

    for b in bookings:
        if not (co <= b[0] or ci >= b[1]):
            return f"❌ Room {room_id} is already booked between {b[0]} and {b[1]}."
    return f"✅ Room {room_id} is available between {ci} and {co}."
