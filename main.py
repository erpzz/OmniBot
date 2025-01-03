import threading
import time
from chatforge import Responder
from sockConnect import SockConnect
from transcript_recorder import TranscriptRecorder
from channelScraper import get_channel_id
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the transcript recorder
transcript_recorder = TranscriptRecorder()


last_channel = None

def listen_to_chat(chat_choice, chat_id, stop_event, bearer_token):
    # Initialize the Responder
    responder = Responder()
    
    sC = SockConnect(chat_choice, chat_id, responder, transcript_recorder, bearer_token)

    try:
        print(f"Listening to chat: {chat_choice}")
        sC.run(stop_event)
    except KeyboardInterrupt:
        print("Stopped listening to the chat.")

def handle_user_input():
    global last_channel

    listener_thread = None
    stop_event = threading.Event()

    while True:
        print("=========================================================================================================")
        print("Author:              yahboy")
        print("Project Title:       AutoChat")
        print("Purpose:             A tool that connects to the kick chat of your choosing and auto responds to messages using OmniBot.")  
        print("=========================================================================================================")
        print("\nMenu:")
        print("1. Activate Omni AI ChatBot")
        # print("2. Stop Listening")
        # print("3. Change Channel")
        # print("4. Reviews and Fine-Tuning")
        # print("5. Start Transcript Recorder")
        # print("6. Quick Resume Last Channel")
        print("7. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            if listener_thread and listener_thread.is_alive():
                print("Already listening to a chat. Please stop the current listener first.")
                continue

            chat_choice = input("Enter chat to scan: ")
            chat_id = get_channel_id(chat_choice)
            bearer_token = input("Enter the bearer token: ").strip()
            if chat_id is None:
                print(f"Unable to proceed without a valid channel ID for {chat_choice}.")
                continue
            
            last_channel = (chat_choice, chat_id)
            listener_thread = threading.Thread(target=listen_to_chat, args=(chat_choice, chat_id, stop_event, bearer_token))
            listener_thread.start()

        elif choice == "2":
            if listener_thread and listener_thread.is_alive():
                stop_event.set()
                listener_thread.join()
                print("Chat listener stopped.")
                stop_event.clear()
            else:
                print("No active chat listener to stop.")

        elif choice == "3":
            if listener_thread and listener_thread.is_alive():
                print("Please stop the current listener before changing the channel.")
            else:
                print("Change Channel selected.")

        elif choice == "4":
            # Review and rate feedback
            Responder.review_feedback()

        elif choice == "5":
            transcript_recorder.toggle_recording()

        elif choice == "6":
            if last_channel:
                chat_choice, chat_id = last_channel
                if listener_thread and listener_thread.is_alive():
                    print("Already listening to a chat. Please stop the current listener first.")
                    continue

                print(f"Resuming chat: {chat_choice}")
                listener_thread = threading.Thread(target=listen_to_chat, args=(chat_choice, chat_id, stop_event, bearer_token))
                listener_thread.start()
            else:
                print("No channel to resume.")

        elif choice == "7":
            if listener_thread and listener_thread.is_alive():
                stop_event.set()
                listener_thread.join()
            print("Exiting the program...")
            break

        else:
            print("Invalid choice. Please enter a number from 1-7.")

if __name__ == "__main__":
    input_thread = threading.Thread(target=handle_user_input)
    input_thread.daemon = True
    input_thread.start()

    while input_thread.is_alive():
        time.sleep(1)
