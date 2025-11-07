# app.py
"""
Streamlit UI for Hotel Booking Assistant.

Features:
- Text input (typed) and voice input (microphone) for queries.
- Safely sync voice recognition into the text input without triggering
  Streamlit's "cannot modify widget key after instantiation" error.
- Run LangChain agent on the query and show response + conversation history.
- Robust error handling for DB, microphone and agent calls.

Key patterns used:
- Initialize session_state keys *before* creating widgets.
- Do NOT assign to a widget-backed session_state key after the widget is created.
  Instead, store voice results in a separate non-widget key (voice_text) and
  create the text_input with value=voice_text on rerun so the widget is initialized
  with the recognized text.
- Use st.rerun() (Streamlit stable API) rather than experimental_rerun().
- Wrap microphone and agent calls with try/except and provide user-friendly messages.
"""

from hotel_chatbort import agent, memory  # central agent + memory (created once)
import os
import streamlit as st
import speech_recognition as sr
from dotenv import load_dotenv
from database.db_connection import get_connection

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # shown for debugging / info if needed

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(page_title="🏨 Hotel Booking Chatbot", page_icon="🤖", layout="centered")

# -------------------------
# Sidebar: Database status
# -------------------------
with st.sidebar:
    st.title("⚙️ System Status")
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
            st.success(f"✅ Connected to PostgreSQL\n{version[0]}")
        finally:
            # Always attempt to close connection if it supports close()
            try:
                conn.close()
            except Exception:
                pass
    except Exception as e:
        # Do not raise — show friendly message
        st.error(f"❌ Database Connection Failed\n{e}")

# -------------------------
# Page header + instructions
# -------------------------
st.title("🏨 Hotel Booking Assistant")
st.markdown(
    """
### 💬 Ask about hotels, rooms, prices, or bookings  
_Example:_
- **Show hotels in Lahore under 100**
- **Available rooms in Pearl Continental**
- **Hotels rated above 4 in Karachi**
"""
)
st.divider()

# -------------------------
# Recognizer (speech input)
# -------------------------
recognizer = sr.Recognizer()

# -------------------------
# Session state initialization
# -------------------------
# voice_text: non-widget key used to store recognized voice text between reruns
# typed_query: widget key used by st.text_input (do NOT overwrite this after the widget is created)
if "voice_text" not in st.session_state:
    st.session_state["voice_text"] = ""
if "typed_query" not in st.session_state:
    # create a placeholder; DO NOT overwrite this later after widget instantiation
    st.session_state["typed_query"] = ""

# -------------------------
# Small helper functions
# -------------------------

def listen_and_recognize(recognizer, timeout=5, phrase_time_limit=10):
    """Listen from default microphone and return recognized text.

    Returns (text, error) where text is a str if success, else ""; error is None or exception/message.
    """
    try:
        with sr.Microphone() as source:
            # optional: adjust for ambient noise to improve recognition stability
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        return "", "listening_timeout"
    except Exception as e:
        return "", f"microphone_error: {e}"

    # Recognize (Google) — network call
    try:
        text = recognizer.recognize_google(audio_data)
        return text, None
    except sr.UnknownValueError:
        return "", "could_not_understand"
    except sr.RequestError:
        return "", "service_unavailable"
    except Exception as e:
        return "", f"recognition_error: {e}"


# -------------------------
# Text input & Voice button
# -------------------------
# Build the text_input with an initial value from voice_text if present.
# This avoids assigning to st.session_state['typed_query'] after widget instantiation,
# which triggers StreamlitAPIException.
initial_value = st.session_state.get("voice_text") or st.session_state.get("typed_query", "")

# Create text_input: the 'value' parameter initializes the widget with voice_text on rerun.
# This is safe because the widget is created with that initial value rather than being overwritten later.
user_query = st.text_input(
    "💭 Type your query:",
    placeholder="e.g., Lahore between 20 and 100",
    key="typed_query",
    value=initial_value,
    help="Type or press 🎤 to speak. If you speak, recognized text will appear here after rerun.",
)

# Voice button: when pressed, perform listening, store recognized text in non-widget key (voice_text), then rerun.
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🎤 Speak"):
        with st.spinner("🎧 Listening — please speak clearly..."):
            voice_text, err = listen_and_recognize(recognizer)
            if err is None and voice_text:
                # Store recognized text in a non-widget session key only
                st.session_state["voice_text"] = voice_text
                st.success(f"🗣️ You said: {voice_text}")
                # Rerun so the text_input widget will be re-created with value=voice_text
                # (we use st.rerun() — the stable API)
                try:
                    st.rerun()
                except Exception:
                    # In case rerun is not available in the installed version, fallback to a no-op
                    pass
            else:
                if err == "listening_timeout":
                    st.error("⏱️ Listening timed out — no speech detected.")
                elif err == "could_not_understand":
                    st.error("😢 Couldn’t understand your voice.")
                elif err == "service_unavailable":
                    st.error("⚠️ Speech recognition service unavailable.")
                elif err and str(err).startswith("microphone_error"):
                    st.error(f"Microphone error: {err.split(':',1)[1]}")
                elif err and str(err).startswith("recognition_error"):
                    st.error("⚠️ Speech recognition failed. Try again.")
                else:
                    st.error("⚠️ Voice recognition failed. Try again or type your query.")

# -------------------------
# Compose the final query
# -------------------------
# Prefer the visible typed_query (user can edit it). If empty and we have voice_text, use that.
# IMPORTANT: Do NOT assign to st.session_state['typed_query'] after widget creation.
# Instead, read the value and fall back to voice_text when needed.
query = (user_query or "").strip()
if not query and st.session_state.get("voice_text"):
    # Use the voice_text value for processing but do NOT write it to the typed_query key (avoid overwrite)
    query = st.session_state.get("voice_text", "").strip()

# -------------------------
# Run the LangChain agent (if query present)
# -------------------------
if query:
    with st.spinner("🔍 Fetching data from database..."):
        try:
            # Use agent.run if available; otherwise fallback to calling agent(...) and extracting result.
            if hasattr(agent, "run"):
                result = agent.run(query)
            else:
                out = agent({"input": query})
                # Agent may return dict with different keys; be defensive.
                if isinstance(out, dict):
                    result = out.get("output") or out.get("output_text") or str(out)
                else:
                    result = str(out)

            st.markdown("### ✅ Response:")
            st.markdown("---")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Error while fetching data from agent:\n{e}")

# -------------------------
# Conversation History (if any)
# -------------------------
try:
    messages = getattr(memory, "chat_memory", None)
    messages_list = getattr(messages, "messages", None) if messages else None

    if messages_list:
        with st.expander("💬 View Conversation History"):
            for msg in messages_list:
                # msg could have .type (LangChain older) or .role (other shapes); be defensive
                role = "🧑‍💻 You"
                if hasattr(msg, "type"):
                    role = "🧑‍💻 You" if getattr(msg, "type") == "human" else "🤖 Bot"
                elif hasattr(msg, "role"):
                    role = "🧑‍💻 You" if getattr(msg, "role") in ("user", "human") else "🤖 Bot"
                content = getattr(msg, "content", str(msg))
                st.markdown(f"**{role}:** {content}")
except Exception:
    # Never crash the UI because of history rendering problems
    pass

# -------------------------
# Footer
# -------------------------
st.divider()
st.caption("Developed by **Muhammad Moaz** | Powered by LangChain, Streamlit & PostgreSQL 🚀")
