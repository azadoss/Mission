import json
import os
from config import SESSION_FILE

def load_session_handle():
    """Load the previous session handle from file.
    
    Returns:
        str or None: The session handle if available, None otherwise
    """
    try:
        if not os.path.exists(SESSION_FILE):
            print("No session file found")
            return None
            
        with open(SESSION_FILE, 'r') as f:
            try:
                data = json.load(f)
                handle = data.get('previous_session_handle')
                if handle:
                    print(f"Loaded previous session handle: {handle[:10]}...")
                return handle
            except json.JSONDecodeError:
                print("Invalid JSON in session file, ignoring")
                return None
    except Exception as e:
        print(f"Error loading session handle: {e}")
        return None

def save_session_handle(handle):
    """Save the session handle to file.
    
    Args:
        handle (str or None): The session handle to save
    """
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump({'previous_session_handle': handle}, f)
            if handle:
                print(f"Saved session handle: {handle[:10]}...")
    except Exception as e:
        print(f"Error saving session handle: {e}")