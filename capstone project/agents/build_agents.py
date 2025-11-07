# agents/build_agents.py

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ------------------------------------------------
# Import all 10 tool functions from /tools folder
# ------------------------------------------------
from tools.search_hotels_by_city import search_hotels_by_city
from tools.search_available_rooms_by_dates import search_available_rooms_by_dates
from tools.get_room_types_and_prices import get_room_types_and_prices
from tools.search_hotels_by_rating import search_hotels_by_rating
from tools.search_hotels_by_price_range import search_hotels_by_price_range
from tools.get_booking_details import get_booking_details
from tools.get_available_rooms import get_available_rooms
from tools.search_hotel_by_name import search_hotel_by_name
from tools.get_hotel_details import get_hotel_details
from tools.check_room_availability_by_dates import check_room_availability_by_dates

# ------------------------------------------------
# Agents map initialization
# ------------------------------------------------
agents_map = {}

# Helper function to create an agent for each tool
def make_agent(tool_func, tool_name, description):
    tool_obj = Tool(name=tool_name, func=tool_func, description=description)
    return initialize_agent(
        tools=[tool_obj],
        llm=llm,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=False
    )

# ------------------------------------------------
# Define agents for each tool
# ------------------------------------------------
agents_map["search_hotels_by_city"] = make_agent(
    search_hotels_by_city,
    "search_hotels_by_city",
    "Use this when user asks to find hotels in a specific city."
)

agents_map["search_available_rooms_by_dates"] = make_agent(
    search_available_rooms_by_dates,
    "search_available_rooms_by_dates",
    "Use this when user wants available rooms between given dates."
)

agents_map["get_room_types_and_prices"] = make_agent(
    get_room_types_and_prices,
    "get_room_types_and_prices",
    "Use this to get different room types and their prices."
)

agents_map["search_hotels_by_rating"] = make_agent(
    search_hotels_by_rating,
    "search_hotels_by_rating",
    "Use this to search hotels by a specific rating or higher."
)

agents_map["search_hotels_by_price_range"] = make_agent(
    search_hotels_by_price_range,
    "search_hotels_by_price_range",
    "Use this to find hotels within a specific price range."
)

agents_map["get_booking_details"] = make_agent(
    get_booking_details,
    "get_booking_details",
    "Use this to get details of a booking by its ID."
)

agents_map["get_available_rooms"] = make_agent(
    get_available_rooms,
    "get_available_rooms",
    "Use this to see available rooms in a hotel."
)

agents_map["search_hotel_by_name"] = make_agent(
    search_hotel_by_name,
    "search_hotel_by_name",
    "Use this to get details of a specific hotel by its name."
)

agents_map["get_hotel_details"] = make_agent(
    get_hotel_details,
    "get_hotel_details",
    "Use this to show all hotel information such as location, rating, and facilities."
)

agents_map["check_room_availability_by_dates"] = make_agent(
    check_room_availability_by_dates,
    "check_room_availability_by_dates",
    "Use this to check if rooms are available for specific dates."
)