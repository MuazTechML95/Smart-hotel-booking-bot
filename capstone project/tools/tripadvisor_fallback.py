import os
import requests
from dotenv import load_dotenv

load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": "tripadvisor16.p.rapidapi.com"
}

# Simple city mapping fallback
CITY_MAP = {
    "lahore": 304554,
    "karachi": 304555,
    "islamabad": 304556,
    "faisalabad": 304557,
    "multan": 304558
}

def tripadvisor_fallback_any_sentence(user_input: str, limit: int = 5):
    """
    Take any user sentence, detect city, fallback to TripAdvisor hotels.
    """
    import re

    # Detect city from user input
    city_found = None
    for city in CITY_MAP.keys():
        if re.search(rf"\b{city}\b", user_input.lower()):
            city_found = city
            break
    if not city_found:
        # Default city if none found
        city_found = "lahore"

    location_id = CITY_MAP[city_found]

    try:
        # Call TripAdvisor API
        url = f"https://tripadvisor16.p.rapidapi.com/api/v1/hotels/searchHotels?locationId={location_id}&limit={limit}"
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        hotels = []

        for item in data.get("data", []):
            name = item.get("name", "N/A")
            rating = item.get("rating", "N/A")
            address = item.get("address", "N/A")
            hotels.append({"name": name, "rating": rating, "address": address})

        if hotels:
            text = "\n".join([f"{h['name']} - Rating: {h['rating']}, Address: {h['address']}" 
                              for h in hotels])
            return f"Here are some hotels in {city_found.title()}:\n\n{text}"
        else:
            return f"No hotels found in {city_found.title()}."

    except Exception as e:
        return f"TripAdvisor API error: {e}"