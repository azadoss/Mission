import asyncio
from config import HOST, PORT
from server import start_server

async def main():
    """Start the WebSocket server and keep it running."""
    server = await start_server(HOST, PORT)
    print("Server started. Press Ctrl+C to stop.")
    
    # Keep running until interrupted
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nServer stopping...")
    finally:
        server.close()
        await server.wait_closed()
        print("Server stopped.")

if __name__ == "__main__":
    asyncio.run(main())