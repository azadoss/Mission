# Enterprise Gemini WebSocket Server

A durable, secure, and refactored WebSocket server to connect to Google Gemini Live.

## Features
- Automatic session resumption with fallback
- Continuous streaming of audio and text
- Robust error handling and logging

## Setup
1. Create `.env` with 
`GEMINI_API_KEY`
`HOST=0.0.0.0`
`PORT=9084`

2. Install dependencies: `pip install -r requirements.txt`.
3. Run server: `python -m main.py`.

## Frontend 
1. $ cd front
2. npm install
3. npm run dev 