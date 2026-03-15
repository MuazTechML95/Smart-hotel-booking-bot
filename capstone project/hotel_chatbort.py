# # hotel_chatbort.py
# import os
# from dotenv import load_dotenv
# import boto3
# import json
# from langchain.agents import initialize_agent, AgentType
# from langchain.memory import ConversationBufferMemory
# from langchain.tools import Tool
# from langchain.llms.base import LLM
# from langchain.schema import LLMResult
# from typing import Optional, List

# # -------------------------
# # Load environment variables
# # -------------------------
# load_dotenv()

# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_REGION = os.getenv("AWS_REGION", "us-east-1")  # default region

# if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
#     raise RuntimeError("AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY not set in environment")

# # -------------------------
# # Initialize Boto3 Bedrock / Nova client
# # -------------------------
# client = boto3.client(
#     "bedrock-runtime",
#     region_name=AWS_REGION,
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY
# )

# # -------------------------
# # Helper function to call Nova
# # -------------------------
# def nova_chat(input_text: str) -> str:
#     """
#     Sends user input to Amazon Nova model and returns response text.
#     """
#     response = client.invoke_model(
#         modelId="amazon.nova-lite-v1:0",  # or "amazon.nova-pro-v1:0"
#         body=json.dumps({"inputText": input_text})
#     )
#     result = json.loads(response["body"])
#     return result.get("outputText", "")

# # -------------------------
# # Tool imports
# # -------------------------
# from tools.search_hotels_by_city import search_hotels_by_city
# from tools.search_available_rooms_by_dates import search_available_rooms_by_dates
# from tools.search_hotels_by_rating import search_hotels_by_rating
# from tools.search_hotels_by_price_range import search_hotels_by_price_range
# from tools.search_hotel_by_name import search_hotel_by_name
# from tools.get_hotel_details import get_hotel_details
# from tools.get_available_rooms import get_available_rooms
# from tools.get_booking_details import get_booking_details
# from tools.check_room_availability_by_dates import check_room_availability_by_dates

# # -------------------------
# # Safe wrapper for rating
# # -------------------------
# def safe_search_hotels_by_rating(min_rating: Optional[float] = None):
#     if min_rating is None:
#         min_rating = 0.0
#     try:
#         min_rating = float(min_rating)
#     except Exception:
#         min_rating = 0.0
#     return search_hotels_by_rating(min_rating)

# # -------------------------
# # Define tools list
# # -------------------------
# tools = [
#     Tool(name="Search Hotels by City", func=search_hotels_by_city,
#          description="Find hotels available in a specific city."),
    
#     Tool(name="Search Available Rooms by Dates", func=search_available_rooms_by_dates,
#          description="Find available rooms between check-in and check-out dates."),
    
#     Tool(name="Search Hotels by Rating", func=safe_search_hotels_by_rating,
#          description="Find hotels with a specific star rating (optional). Only use if user mentions rating explicitly."),
    
#     Tool(name="Search Hotels by Price Range", func=search_hotels_by_price_range,
#          description="Find hotels within a specific price range."),
    
#     Tool(name="Search Hotel by Name", func=search_hotel_by_name,
#          description="Find a hotel by its name."),
    
#     Tool(name="Get Hotel Details", func=get_hotel_details,
#          description="Retrieve detailed information about a specific hotel."),
    
#     Tool(name="Get Available Rooms", func=get_available_rooms,
#          description="Get all currently available rooms for a given hotel."),
    
#     Tool(name="Get Booking Details", func=get_booking_details,
#          description="Retrieve booking details by booking ID."),
    
#     Tool(name="Check Room Availability by Dates", func=check_room_availability_by_dates,
#          description="Check room availability for specific dates."),
# ]

# # -------------------------
# # Conversation memory
# # -------------------------
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # -------------------------
# # LangChain wrapper for Nova
# # -------------------------
# class NovaLLM(LLM):
#     """LangChain wrapper for Amazon Nova"""
#     @property
#     def _llm_type(self) -> str:
#         return "nova"

#     def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
#         return nova_chat(prompt)

#     def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
#         outputs = [nova_chat(p) for p in prompts]
#         return LLMResult(generations=[[{"text": o}] for o in outputs])

#     async def _agenerate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
#         outputs = [nova_chat(p) for p in prompts]
#         return LLMResult(generations=[[{"text": o}] for o in outputs])

# # -------------------------
# # Initialize LLM
# # -------------------------
# llm = NovaLLM()

# # -------------------------
# # Initialize LangChain agent
# # -------------------------
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent_type=AgentType.OPENAI_FUNCTIONS,  # keep same for tool calling
#     memory=memory,
#     verbose=False
# )

# hotel_chatbot_nova.py
import os
import json
from dotenv import load_dotenv
import boto3
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from langchain.llms.base import LLM
from langchain.schema import LLMResult
from typing import Optional, List
from tools.tripadvisor_fallback import tripadvisor_fallback_any_sentence 

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# -------------------------
# Initialize Amazon Nova client (via Bedrock)
# -------------------------
client = boto3.client(
    "bedrock-runtime",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# -------------------------
# Nova chat function
# -------------------------
def nova_chat(input_text: str) -> str:
    """Send input to Nova 2 Lite and get response."""
    response = client.invoke_model(
        modelId="amazon.nova-lite-v1:0",
        body=json.dumps({"inputText": input_text})
    )
    result = json.loads(response["body"])
    return result.get("outputText", "")

# -------------------------
# Import hotel tools
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
# Safe wrapper for rating
# -------------------------
def safe_search_hotels_by_rating(min_rating: Optional[float] = None):
    try:
        min_rating = float(min_rating or 0.0)
    except:
        min_rating = 0.0
    return search_hotels_by_rating(min_rating)

# -------------------------
# Define tools list
# -------------------------
tools = [
    Tool(name="Search Hotels by City", func=search_hotels_by_city, description="Find hotels in a specific city."),
    Tool(name="Search Available Rooms by Dates", func=search_available_rooms_by_dates, description="Get available rooms between dates."),
    Tool(name="Search Hotels by Rating", func=safe_search_hotels_by_rating, description="Find hotels above a rating."),
    Tool(name="Search Hotels by Price Range", func=search_hotels_by_price_range, description="Find hotels in a price range."),
    Tool(name="Search Hotel by Name", func=search_hotel_by_name, description="Find a hotel by its name."),
    Tool(name="Get Hotel Details", func=get_hotel_details, description="Retrieve hotel details."),
    Tool(name="Get Available Rooms", func=get_available_rooms, description="Get available rooms for a hotel."),
    Tool(name="Get Booking Details", func=get_booking_details, description="Retrieve booking details."),
    Tool(name="Check Room Availability by Dates", func=check_room_availability_by_dates, description="Check room availability by dates."),
]

# -------------------------
# Conversation memory
# -------------------------
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# -------------------------
# LangChain LLM wrapper for Nova
# -------------------------
class NovaLLM(LLM):
    @property
    def _llm_type(self) -> str:
        return "nova"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        return nova_chat(prompt)

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None) -> LLMResult:
        outputs = [nova_chat(p) for p in prompts]
        return LLMResult(generations=[[{"text": o}] for o in outputs])

# -------------------------
# Initialize LLM & agent
# -------------------------
llm = NovaLLM()
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    memory=memory,
    verbose=False
)
def safe_nova_chat(input_text: str) -> str:
    """
    Try Nova LLM. If permission / ValidationException fails, use TripAdvisor API fallback.
    """
    try:
        # Try Nova first
        response = nova_chat(input_text)  # your existing Nova call
        if response.strip() == "":
            raise Exception("Empty response")
        return response
    except Exception as e:
        print(f"⚠️ Nova failed: {e}, using TripAdvisor fallback...")
        
        # Simple fallback: check if query mentions city
        import re
        city_match = re.search(r"in (\w+)", input_text.lower())
        city = city_match.group(1) if city_match else "Lahore"
        fallback_result = tripadvisor_fallback_any_sentence(city)
        
        # Format nicely
        if isinstance(fallback_result, list):
            text = "\n".join([f"{h['name']} - Rating: {h['rating']}, Address: {h['address']}" for h in fallback_result])
            return f"⚠️ Nova unavailable. Showing TripAdvisor results instead:\n\n{text}"
        else:
            return f"⚠️ Nova unavailable. {fallback_result}"