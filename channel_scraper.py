# From: Eric Paiz
from chatforge import Responder
from sockConnect import SockConnect
from chat_database import ChatDatabase
import websocket
import json
import time
import threading 

# Initialize the database
db = ChatDatabase()

# Feedback log file for review and fine-tuning
feedback_log_file = "feedback_log.json"

def get_channel_id_from_websocket(streamer_name):
    # Attempt to get channel ID from WebSocket traffic
    channel_id = None
    start_time = time.time()  # Start time for timeout calculation

    def on_message(ws, message):
        nonlocal channel_id
        try:
            data = json.loads(message)
            # Extract channel information from the subscription events
            if data.get("event") == "pusher_internal:subscription_succeeded" and "chatrooms" in data.get("channel", ""):
                channel_id = data["channel"].split(".")[1]  # Assuming the format is 'chatrooms.<channel_id>.v2'
                ws.close()
        except json.JSONDecodeError:
            pass

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    ws_url = "wss://ws-us2.pusher.com/app/32cbd69e4b950bf97679?protocol=7&client=js&version=8.4.0-rc28&flash=false"
    ws_app = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    # Run WebSocket with a timeout of 15 seconds
    try:
        ws_thread = threading.Thread(target=ws_app.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        while time.time() - start_time < 15:
            if channel_id is not None:
                break
            time.sleep(1)  # Polling interval

        if channel_id is None:
            print("Timeout reached while attempting to get channel ID from WebSocket.")
    except Exception as e:
        print(f"Error during WebSocket connection: {e}")

    return channel_id

def get_channel_id(streamer_name):
    # First try to get channel ID from the database
    channel_id = db.get_channel_id(streamer_name)
    if channel_id:
        print(f"Found channel ID for {streamer_name} in database: {channel_id}")
        return channel_id

    # Attempt to get channel ID from WebSocket traffic
    print("Attempting to get channel ID from WebSocket traffic...")
    channel_id = get_channel_id_from_websocket(streamer_name)
    if channel_id:
        print(f"Retrieved channel ID for {streamer_name} from WebSocket: {channel_id}")
        db.insert_streamer(streamer_name, channel_id)
        return channel_id

    # If not found in WebSocket, prompt user for manual entry
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        channel_id = input(f"Unable to retrieve the channel ID for '{streamer_name}'. Please enter the channel ID manually: ")
        if channel_id.isdigit():
            channel_id = int(channel_id)
            # Save manually entered channel ID to the database
            db.insert_streamer(streamer_name, channel_id)
            return channel_id
        else:
            print("Invalid channel ID entered. Please enter a numeric channel ID.")
            retry_count += 1

    print("Maximum retries reached. Unable to retrieve a valid channel ID.")
    return None

def review_feedback():
    try:
        with open(feedback_log_file, "r") as log_file:
            print("=== Reviews and Fine-Tuning ===")
            for line in log_file:
                feedback_entry = json.loads(line)
                print(f"Chat Message: {feedback_entry['chat_message']}")
                print(f"Response: {feedback_entry['response']}")
                print(f"Rating: {feedback_entry['rating']}")
                print("----------------------------------------")
                # Prompt user to adjust rating or log improvement if needed
                new_rating = input("Enter new rating (or press Enter to keep current): ")
                if new_rating.isdigit() and 1 <= int(new_rating) <= 5:
                    feedback_entry['rating'] = int(new_rating)
                    # Re-log updated feedback entry
                    with open(feedback_log_file, "a") as update_log:
                        update_log.write(json.dumps(feedback_entry) + "\n")
    except FileNotFoundError:
        print("No feedback log file found.")
    except Exception as e:
        print(f"Error during review: {e}")
