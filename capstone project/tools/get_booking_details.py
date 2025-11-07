from langchain.tools import tool
from database.db_connection import get_connection

@tool("get_booking_details", return_direct=True)
def get_booking_details(booking_id: int) -> str:
    """Retrieve booking details by booking ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, h.name, hr.room_number, b.check_in, b.check_out, b.status
        FROM bookings b
        JOIN hotel_rooms hr ON b.room_id = hr.id
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE b.id = %s;
    """, (booking_id,))
    booking = cur.fetchone()
    cur.close()
    conn.close()
    if not booking:
        return f"No booking found with ID {booking_id}."
    return f"Booking #{booking[0]} — {booking[1]} Room {booking[2]}, {booking[3]} to {booking[4]} — Status: {booking[5]}"
