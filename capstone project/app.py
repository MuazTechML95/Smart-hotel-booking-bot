# app_nova
import os
import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from hotel_chatbort import agent, memory
from database.db_connection import get_connection
from boto3 import client as boto3_client
import json

# -------------------------
# Load env variables
# -------------------------
load_dotenv()
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(page_title="🏨 Hotel Booking Assistant (Nova)", page_icon="🤖", layout="centered")

# -------------------------
# Sidebar: DB status
# -------------------------
with st.sidebar:
    st.title("Ditail Hotels 🏨")
    try:
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
        st.success(f"✅ Connected to PostgreSQL\n{version[0]}")
        conn.close()
    except Exception as e:
        st.error(f"❌ Database Connection Failed\n{e}")

# -------------------------
# Page header
# -------------------------
st.title("🏨 Hotel Booking Assistant (Nova)")
st.markdown("""
### 💬 Ask about hotels, rooms, prices, or bookings
_Example queries:_  
- Show hotels in Lahore under 100  
- Available rooms in Pearl Continental  
- Hotels rated above 4 in Karachi
""")
st.divider()

# -------------------------
# Speech recognizer
# -------------------------
recognizer = sr.Recognizer()
if "voice_text" not in st.session_state: st.session_state["voice_text"] = ""
if "typed_query" not in st.session_state: st.session_state["typed_query"] = ""

def listen_and_recognize(recognizer, timeout=5, phrase_time_limit=10):
    """Use Nova 2 Sonic for voice-to-text (pseudo-code)"""
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        return "", "listening_timeout"
    except Exception as e:
        return "", f"microphone_error: {e}"

    try:
        # Replace with actual Nova 2 Sonic integration
        text = agent.run(f"[Voice Input] Convert speech to text: {audio_data}")
        return text, None
    except Exception as e:
        return "", f"recognition_error: {e}"

# -------------------------
# User input
# -------------------------
initial_value = st.session_state.get("voice_text") or st.session_state.get("typed_query", "")
user_query = st.text_input("💭 Type your query:", placeholder="e.g., Lahore between 20 and 100",
                           key="typed_query", value=initial_value,
                           help="Type or press 🎤 to speak. Recognized voice text will appear here.")

col1, col2 = st.columns([4,1])
with col2:
    if st.button("🎤 Speak"):
        with st.spinner("🎧 Listening..."):
            voice_text, err = listen_and_recognize(recognizer)
            if err is None and voice_text:
                st.session_state["voice_text"] = voice_text
                st.success(f"🗣️ You said: {voice_text}")
                st.rerun()
            else:
                st.error(f"⚠️ Voice recognition failed: {err}")

# -------------------------
# Final query
# -------------------------
query = (user_query or "").strip() or st.session_state.get("voice_text", "").strip()

# -------------------------
# Run agent for query
# -------------------------
from tools.tripadvisor_fallback import tripadvisor_fallback_any_sentence

if query:
    with st.spinner("🔍 Fetching results..."):
        try:
            # Try Nova agent first
            result = agent.run(query)
            if not result.strip():
                raise Exception("Nova empty response")
            st.markdown("### ✅ Response:")
            st.markdown("---")
            st.write(result)

        except Exception:
            # Nova fail → fallback silently
            fallback_result = tripadvisor_fallback_any_sentence(query)
            st.markdown("### ✅ Response:")
            st.markdown("---")
            st.write(fallback_result)

# -------------------------
# Show conversation history
# -------------------------
try:
    messages_list = getattr(memory.chat_memory, "messages", [])
    if messages_list:
        with st.expander("💬 View Conversation History"):
            for msg in messages_list:
                role = "🧑‍💻 You" if getattr(msg,"role","user") in ("user","human") else "🤖 Bot"
                content = getattr(msg,"content",str(msg))
                st.markdown(f"**{role}:** {content}")
except Exception:
    pass

st.divider()
st.caption("Developed by **Muhammad Moaz** | Powered by Amazon Nova, Streamlit & PostgreSQL 🚀")