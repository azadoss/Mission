gemini_live_server/
│
├── .env                        # Environment variables
├── main.py                     # Entry point for the application  
├── requirements.txt            # Project dependencies
│
├── app/
│   ├── __init__.py             # Makes app a package
│   ├── config.py               # Configuration settings
│   ├── gemini_client.py        # Gemini API client setup
│   ├── session_manager.py      # Handles session persistence
│   └── websocket_server.py     # WebSocket server implementation
│
└── logs/                       # Directory for logs