# hotel_chatbort.py
import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI 
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from typing import Optional

# -------------------------
# Load environment
# -------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set in environment")

# -------------------------
# Initialize LLM
# -------------------------
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

# -------------------------
# Tool functions (import)
# -------------------------
from tools.search_hotels_by_city import search_hotels_by_city
from tools.search_available_rooms_by_dates import search_available_rooms_by_dates
from tools.search_hotels_by_rating import search_hotels_by_rating
from tools.search_hotels_by_price_range import search_hotels_by_price_range
from tools.search_hotel_by_name import search_hotel_by_name
from tools.get_hotel_details import get_hotel_details
from tools.get_available_rooms import get_available_rooms
from tools.get_booking_details import get_booking_details
from tools.check_room_availability_by_dates import check_room_availability_by_dates

# -------------------------
# Wrap rating tool to make it safe
# -------------------------
def safe_search_hotels_by_rating(min_rating: Optional[float] = None):
    """
    Safe wrapper: If agent calls without rating, default to 0.
    Converts string inputs to float.
    """
    if min_rating is None:
        min_rating = 0.0
    try:
        min_rating = float(min_rating)
    except Exception:
        min_rating = 0.0
    return search_hotels_by_rating(min_rating)

# -------------------------
# Define tools list
# -------------------------
tools = [
    Tool(name="Search Hotels by City", func=search_hotels_by_city,
         description="Find hotels available in a specific city."),
    
    Tool(name="Search Available Rooms by Dates", func=search_available_rooms_by_dates,
         description="Find available rooms between check-in and check-out dates."),
    
    Tool(name="Search Hotels by Rating", func=safe_search_hotels_by_rating,
         description="Find hotels with a specific star rating (optional). Only use if user mentions rating explicitly."),
    
    Tool(name="Search Hotels by Price Range", func=search_hotels_by_price_range,
         description="Find hotels within a specific price range."),
    Tool(name="Search Hotel by Name", func=search_hotel_by_name,
         description="Find a hotel by its name."),
    
    Tool(name="Get Hotel Details", func=get_hotel_details,
         description="Retrieve detailed information about a specific hotel."),
    
    Tool(name="Get Available Rooms", func=get_available_rooms,
         description="Get all currently available rooms for a given hotel."),
    
    Tool(name="Get Booking Details", func=get_booking_details,
         description="Retrieve booking details by booking ID."),
    
    Tool(name="Check Room Availability by Dates", func=check_room_availability_by_dates,
         description="Check room availability for specific dates."),
]

# -------------------------
# Conversation memory
# -------------------------
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# -------------------------
# Initialize agent
# -------------------------
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    memory=memory,
    verbose=False
)