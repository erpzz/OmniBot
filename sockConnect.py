# Developer: Eric Neftali Paiz
import requests
import json
from datetime import datetime, timedelta
import websocket
import re
import time
import random

class SockConnect:
    def __init__(self, chat_name, chat_id, responder, transcript_recorder, bearer_token=None):
        self.bearer_token = bearer_token
        self.chat_name = chat_name  # Streamer's chatroom name
        self.chat_id = chat_id  # Chatroom ID
        self.ws_url = "wss://ws-us2.pusher.com/app/32cbd69e4b950bf97679?protocol=7&client=js&version=8.4.0-rc28&flash=false"
        self.responder = responder
        self.api_url = f"https://kick.com/api/v2/messages/send/{chat_id}"
        # Use the below to change the response time
        self.last_response_time = datetime.utcnow() - timedelta(seconds=5)
        self.transcript_recorder = transcript_recorder
        self.bot_name = "Omni"  # Initially set bot name to None

    def send_message_via_api(self, response):
        try:
            payload = {
                "chatroom_id": self.chat_id,
                "content": response,
                "type": "message"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.1",
                "Origin": "https://kick.com",
                "Referer": f"https://kick.com/{self.chat_name}"
            }

            response = requests.post(self.api_url, headers=headers, json=payload)

            if response.status_code == 200:
                response_data = response.json()
                if not response_data["status"]["error"]:
                    print(f"Message sent successfully: {response_data['data']['content']}")
                    if not self.bot_name:
                        self.bot_name = response_data['data']['sender']['username']  # Set bot name
                else:
                    print(f"Error sending message: {response_data['status']['message']}")
            else:
                print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print(f"Error sending message via API: {e}")

    def on_message(self, ws, message):
        try:
            print(f"Received message: {message}")
            data = json.loads(message)
            if data.get("event") == "App\\Events\\ChatMessageEvent":
                message_data = json.loads(data["data"])
                content = message_data["content"]
                sender = message_data["sender"]["username"]

                 

                # Ignore the bot's own messages
                if self.bot_name and sender.lower() == self.bot_name.lower():
                    print(f"Ignoring bot's own message: {content}")
                    return


                # Check if the bot is mentioned
                bot_mentioned = self.bot_name.lower() in content.lower() or f"@{self.bot_name.lower()}" in content.lower()

                if bot_mentioned:
                    print(f"Bot mentioned in message: {content}")
                    response = self.responder.artificialChatter(
                        chat_message=content,
                        sender_name=sender,
                        streamer_name=self.chat_name,
                        bot_name=self.bot_name or "DefaultBotName"
                    )
                    if response:
                        print(f"AutoResponse to mention: {response}")
                        self.send_message_via_api(response)
                        self.transcript_recorder.write_message(content)
                        self.last_response_time = datetime.utcnow()
                        return

                # Ignore messages from blocked bots
                if sender.lower() in ["kickbot", "botrix"]:
                    print(f"Ignoring message from {sender}: {content}")
                    return

                # Cooldown check
                current_time = datetime.utcnow()
                if (current_time - self.last_response_time).total_seconds() < 5:
                    print("Ignoring message due to cooldown period.")
                    return

                # Generate a response
                response = self.responder.artificialChatter(content, sender_name=sender, streamer_name=self.chat_name, bot_name=self.bot_name)
                if response:
                    print(f"Received: {content}")
                    print(f"AutoResponse: {response}")
                    self.send_message_via_api(response)
                    self.last_response_time = current_time
                    self.transcript_recorder.write_message(content)

        except json.JSONDecodeError:
            print(f"Raw message received: {message}")
        except Exception as e:
            print(f"Error processing message: {e}")

    def on_open(self, ws):
        print("WebSocket connection opened. Subscribing to channel...")
        subscription_payload = {
            "event": "pusher:subscribe",
            "data": {
                "auth": "",
                "channel": f"chatrooms.{self.chat_id}.v2"
            }
        }
        ws.send(json.dumps(subscription_payload))

    def on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket connection closed: {close_status_code}, {close_msg}")

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def run(self, stop_event):
        websocket.enableTrace(False)
        ws_app = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
        )

        while not stop_event.is_set():
            ws_app.run_forever()
            time.sleep(1)
