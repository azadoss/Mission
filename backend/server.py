import asyncio
import json
import base64
import datetime
import websockets.server
from google.genai import types

from config import MODEL, VOICE_NAME, LANGUAGE_CODE, SYSTEM_INSTRUCTION
from session_manager import load_session_handle, save_session_handle
from gemini_client import create_client

# Create Gemini client
client = create_client()

async def handle_websocket_connection(websocket):
    """Handle a WebSocket connection from a client."""
    print(f"Client connected: {websocket.remote_address}")
    
    try:
        # Load the session handle
        session_handle = load_session_handle()

        # Receive initial configuration from client
        config_message = await websocket.recv()
        config_data = json.loads(config_message)
        print(f"Received client configuration")

        
        # Try to connect with existing session or create new one
        await connect_to_gemini(websocket, session_handle)

    except websockets.ConnectionClosed:
        print("Client disconnected")    
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected normally")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Client connection closed unexpectedly: {e}")
    except Exception as e:
        print(f"[{datetime.datetime.now()}] Error in WebSocket connection: {e}")
        try:
            await websocket.send(json.dumps({"error": str(e)}))
        except:
            pass
    finally:
        print(f"Connection closed: {websocket.remote_address}")

async def connect_to_gemini(websocket, session_handle=None):
    """Connect to Gemini API with an optional session handle."""
    # First try with the provided handle
    try:
        await start_gemini_session(websocket, session_handle)
    except Exception as e:
        if session_handle and ("session not found" in str(e).lower() or "policy violation" in str(e).lower()):
            print(f"Session error: {e}, retrying with new session")
            # Clear invalid session handle from storage
            save_session_handle(None)  # Add this line
            # If the session is invalid, try again with a new session
            await start_gemini_session(websocket, None)
        else:
            # Other errors should be propagated
            raise

async def start_gemini_session(websocket, session_handle):
    """Start a Gemini session with the given handle."""
    # Create session configuration
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME)
            ),
            language_code=LANGUAGE_CODE,
        ),
        system_instruction=SYSTEM_INSTRUCTION,
        session_resumption=types.SessionResumptionConfig(
            handle=session_handle
        ),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    # Connect to Gemini API
    async with client.aio.live.connect(model=MODEL, config=config) as session:
        print(f"Connected to Gemini API" + (f" with handle: {session_handle[:10]}..." if session_handle else " with new session"))
        
        # Create sender and receiver tasks
        send_task = asyncio.create_task(send_to_gemini(websocket, session))
        receive_task = asyncio.create_task(receive_from_gemini(websocket, session))
        
        try:
            done, pending = await asyncio.wait(
                [send_task, receive_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                
            await asyncio.gather(*pending, return_exceptions=True)
            
        except asyncio.CancelledError:
            # Handle explicit cancellation
            send_task.cancel()
            receive_task.cancel()
            await asyncio.gather(send_task, receive_task, return_exceptions=True)

async def send_to_gemini(websocket, session):
    """Send data from WebSocket client to Gemini."""
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                # Handle start/stop commands FIRST
                if "action" in data:
                    if data["action"] == "start_sharing":
                        print("Screen sharing started")
                        # Close session first
                        await session.close()
                        # Then break out of the loop
                        break
                    elif data["action"] == "stop_sharing":
                        print("Screen sharing stopped")
                        await session.close()
                        return
                
                # Then handle media/text as before
                if "realtime_input" in data:
                    for chunk in data["realtime_input"]["media_chunks"]:
                        await session.send(input={
                            "mime_type": chunk["mime_type"],
                            "data": chunk["data"]
                        })
                
                # Handle text input
                elif "text" in data:
                    text_content = data["text"]
                    print(f"Sending text to Gemini: {text_content[:50]}...")
                    await session.send(input={
                        "mime_type": "text/plain",
                        "data": text_content
                    })
                    
            except Exception as e:
                print(f"Error sending to Gemini: {e}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected while sending")
    except asyncio.CancelledError:
        print("Send task cancelled")
    except Exception as e:
        print(f"Error in send_to_gemini: {e}")
    finally:
        print("Send task completed")

async def receive_from_gemini(websocket, session):
    """Receive data from Gemini and send it to the WebSocket client."""
    try:
        # Continuous loop to keep receiving from Gemini until connection is closed
        keep_receiving = True
        while keep_receiving:
            try:
                async for response in session.receive():
                    # Handle interruptions
                    if response.server_content and hasattr(response.server_content, 'interrupted') and response.server_content.interrupted is not None:
                        print(f"[{datetime.datetime.now()}] Generation interrupted")
                        await websocket.send(json.dumps({"interrupted": "True"}))
                        continue

                    # Log token usage
                    if response.usage_metadata:
                        usage = response.usage_metadata
                        print(f'Used {usage.total_token_count} tokens in total.')

                    # Handle session resumption updates
                    if response.session_resumption_update:
                        update = response.session_resumption_update
                        if update.resumable and update.new_handle:
                            save_session_handle(update.new_handle)
                            print(f"Updated session handle")

                    # Handle output transcription (assistant's speech)
                    if response.server_content and hasattr(response.server_content, 'output_transcription') and response.server_content.output_transcription is not None:
                        await websocket.send(json.dumps({
                            "transcription": {
                                "text": response.server_content.output_transcription.text,
                                "sender": "Gemini",
                                "finished": response.server_content.output_transcription.finished
                            }
                        }))
                    
                    # Handle input transcription (user's speech)
                    if response.server_content and hasattr(response.server_content, 'input_transcription') and response.server_content.input_transcription is not None:
                        await websocket.send(json.dumps({
                            "transcription": {
                                "text": response.server_content.input_transcription.text,
                                "sender": "User",
                                "finished": response.server_content.input_transcription.finished
                            }
                        }))

                    # Skip empty responses
                    if response.server_content is None:
                        continue
                        
                    # Handle model's text and audio responses
                    model_turn = response.server_content.model_turn
                    if model_turn:
                        for part in model_turn.parts:
                            if hasattr(part, 'text') and part.text is not None:
                                await websocket.send(json.dumps({"text": part.text}))
                            
                            elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                try:
                                    audio_data = part.inline_data.data
                                    base64_audio = base64.b64encode(audio_data).decode('utf-8')
                                    await websocket.send(json.dumps({
                                        "audio": base64_audio,
                                    }))
                                except Exception as e:
                                    print(f"Error processing assistant audio: {e}")

                    # Handle turn completion
                    if response.server_content and response.server_content.turn_complete:
                        print('\n<Turn complete>')
                        await websocket.send(json.dumps({
                            "transcription": {
                                "text": "",
                                "sender": "Gemini",
                                "finished": True
                            }
                        }))
                
                # After one iteration is completed, continue listening for the next response
                print("Waiting for next user input...")
                
            except asyncio.CancelledError:
                print("Receive task was cancelled")
                #keep_receiving = False
            except Exception as e:
                print(f"Error in receive loop: {e}")
                # Don't exit the loop for errors that might be temporary
                await asyncio.sleep(1)  # Small delay before retrying
                
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected while receiving")
    except Exception as e:
        print(f"Error in receive_from_gemini: {e}")
    finally:
        print("Receive task completed")

async def start_server(host, port):
    """Start the WebSocket server."""
    server = await websockets.server.serve(
        handle_websocket_connection,
        host=host,
        port=port,
        origins=None,  # Allow all origins
        compression=None,  # Disable compression to avoid deprecation warning
        ping_interval=30,  # Send ping frames every 30 seconds
        ping_timeout=10    # Wait 10 seconds for pong response
    )
    
    print(f"WebSocket server running on {host}:{port}")
    return server