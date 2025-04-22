import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# API settings
# Ensure GOOGLE_API_KEY is set in your environment variables or .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    # Use logger from main or raise an error early
    print("Error: GEMINI_API_KEY not found in environment variables")
    # In a production app, you might raise an exception or exit here.
    # For debugging, print and let the client creation potentially fail.

# Model settings
MODEL = "gemini-2.0-flash-live-001" # Or your chosen Live API model
VOICE_NAME = "Charon" # Or your preferred voice Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr.
LANGUAGE_CODE = "en-US" # Or your preferred language code
SYSTEM_INSTRUCTION = "You are a helpful assistant." # Or your system instruction

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 9084))

# Session file path
SESSION_FILE = "session_handle.json" # File to save the session handle