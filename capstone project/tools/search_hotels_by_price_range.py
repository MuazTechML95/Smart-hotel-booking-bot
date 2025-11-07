from langchain.tools import tool
from database.db_connection import get_connection
import re

@tool("search_hotels_by_price_range", return_direct=True)
def search_hotels_by_price_range(query: str) -> str:
    """
    Search hotels in a city within the mentioned price range.
    Example input: 'Lahore between 20 and 100'
    """
    # Extract numeric price values from text
    prices = re.findall(r'\d+', query)
    if len(prices) < 2:
        return "⚠️ Please mention a valid price range, e.g., 'Lahore between 200 and 1000'."
    
    # Extract and clean city name
    city_name = re.sub(r'\d+', '', query).replace('between', '').replace('and', '').strip()
    min_price, max_price = map(float, prices[:2])

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT h.name, h.city, hr.price_per_night
        FROM hotels h
        JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE h.city ILIKE %s AND hr.price_per_night BETWEEN %s AND %s;
    """, (f"%{city_name}%", min_price, max_price))
    hotels = cur.fetchall()
    cur.close()
    conn.close()

    # Return results
    if not hotels:
        return f"❌ No hotels found in {city_name} with price between ₹{min_price}–₹{max_price}."

    formatted_results = "\n".join([
        f"🏨 {h[0]} ({h[1]}) — 💰 ₹{h[2]:,.2f}" for h in hotels
    ])
    return f"✅ Hotels in {city_name} (₹{min_price}–₹{max_price}):\n\n{formatted_results}"
