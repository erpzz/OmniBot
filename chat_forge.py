# Developer: Eric Neftali Paiz
import requests
import ollama
import json
import random
import re
from collections import Counter
from datetime import datetime, timedelta

class Responder:
    def __init__(self, chat_id=None, bot_name=None):
        self.feedback_log = "feedback_log.json"
        self.chat_id = chat_id  # ID for the chatroom
        self.bot_name = bot_name  # Bot's name in the chat
        self.emote_tracker = {}  # Tracks emote occurrences
        self.message_counter = Counter()  # Tracks occurrences of each message
        self.message_reset_time = timedelta(seconds=30)  # Reset tracking after this time
        self.last_reset_time = datetime.utcnow()  # Last time message counter was reset
        # The default responses are a little basic, but this will change in the future. This was created as a side project to serve as a very basic POC to prove to myself that I could make it work.
        self.default_responses = [
            "W", "😂", "???", "It's over.", "You're cooked.", "bro fr?", "lmao", "nah", "wym", "wtf", "😂😂😂", "pause", "no way", "wut"
        ]  # Random fallback responses that mimic casual internet slang.

        # Initialize dynamic weights
        self.emotes_weight = 0.3
        self.common_phrases_weight = 0.2
        self.ollama_response_weight = 0.50

    def artificialChatter(self, chat_message, sender_name, streamer_name, bot_name):
        """
        Generates a response using the Ollama model, customizing the tone and style to fit the chatroom.
        Avoids any AI-like behavior and focuses on natural, human-like responses.
        """
        # Automatically pass the bot's own name if it wasn't already provided
        if not self.bot_name:
            self.bot_name = bot_name  # Set as a default if not provided, but ideally this should be auto-detected

        # Track message frequency and adjust weights if necessary
        should_repeat = self.track_message_frequency(chat_message)
        if should_repeat:
            print(f"Repeating popular message: {chat_message}")
            return chat_message

        # Adjust weights dynamically based on chat trends
        self.adjust_weights_for_popularity()

        # System prompt setting the context for the bot
        system_prompt = f"""
            You are a participant in a live chat. Your name in this chat is "{self.bot_name}", and this is "{streamer_name}"s stream
            - Analyze the ongoing chat messages to maintain the tone and style of the room.
            - Respond appropriately and naturally, mimicking the language style, tone, and humor commonly used in the chat.
            - Only use a sender's name (e.g., "@{sender_name}") if you are tagged directly or responding to their specific query.
            - Avoid generic responses, AI-like behavior, and content moderation messages. Never reference being an AI.
            - Ignore messages that accuse you of being a bot unless explicitly addressed.
            - Responses should be short, informal, and casual—limited to a maximum of 100 characters.
            - Use common chat slang, references, and emotes when responding, to appear as a regular member of the chat.
            - Do not provide lengthy or over-elaborate answers, stay within common chat language expectations.
        """

        # Dynamic prompt combining system message and user input
        prompt = f"""
        {system_prompt}

        New Message:
        "{chat_message}"

        Your Response:
        """

        # Handle bot-detection messages or irrelevant keywords
        bot_keywords = ["bot", "are you real", "ai", "robot", "automated", "real person"]
        if any(keyword in chat_message.lower() for keyword in bot_keywords):
            return None  # Skip responding to these messages

        # Common fallback phrases used in popular chat environments
        common_phrases = [
            # Common Short Phrases
            "sheesh", "bro's wildin", "nah, fr?", "u tweakin", "ain't no way", "W", "L", "no shot", "for real",
            "smh", "yo", "sussy", "bet", "no shot", "rip", "lol", "gg", "ez", "deadass", 
             "wild", "lit", "fr?", "yikes", "big W", "no Ls", "cringe", "based", 

            # Playful Sarcasm and Humor
            "oh, really? couldn't tell 🙄", "man's got jokes", "ok, buddy", "groundbreaking", "bro thinks he's him",
            "you good?", "touch grass", "wow, so deep 😭", "bro's in his villain arc", "ain't nobody care",
            "bruh moment", "bro woke up and chose violence", "sure thing, philosopher", "bro thinks he's Einstein",
            "you for real?", "bro, it's not that deep", "someone's overcompensating", "ok, I guess", "🤡", "yo, chill",
            
            # Meme References and Kick Emotes
            ]
        emotes = [
                "KEKW",  "politeCat", "KEKLEO", "emojiCry", "PeepoClap", "kkHuh","HYPERCLAPH", "POLICE", "NONTENT", "WeSmart", "mericKat", "emojiLol" "peepoRiot", "LUL", "OMEGALUL",
                "Copium", "EZ Clap", "POGGERS", "Sadge","ResidentSleeper", "emojiDead", 
                "GIGACHAD",
                "WeirdChamp", "MODS","NODDERS", "YIKES", "PatrickBoo",
            ]
        categories = ["emotes", "common_phrases", "ollama_response"]
        probabilities = [self.emotes_weight, self.common_phrases_weight, self.ollama_response_weight]
        response_text = None 
        try:  
            # Randomly choose to send a common phrase, an emote, or generate a response using Ollama
            chosen_category = random.choices(categories, weights=probabilities, k=1)[0]

            if chosen_category == "emotes":
                response_text = "[emote:37226:KEKW]"
            elif chosen_category == "common_phrases":
                response_text = "[emote:37226:KEKW]"
            elif chosen_category == "ollama_response":
                # Generate response using the Ollama model
                response_text = "[emote:37226:KEKW]"

            # Handle content moderation cases
            if response_text and ("cannot create explicit content" in response_text.lower() or "cannot create content" in response_text.lower()):
                return random.choice(common_phrases)

            # Clean response of unnecessary quotes
            response_text = self.clean_response(response_text)

            # Log response for feedback review
            self.log_feedback(chat_message, response_text)

            # Return the response, ensuring it's within character limits
            return response_text[:100]

        except Exception as e:
            print(f"Error generating response with Ollama: {e}")

            # Return a random fallback response if Ollama fails
            return random.choice(self.default_responses)

    def generate_with_ollama(self, prompt):
        """
        Generates a response using the Ollama model.
        """
        try:
            response = ollama.generate(
                model="llama3:latest",  # Replace with your actual model
                prompt=prompt
            )
            return response.get("response", "No response generated.")
        except Exception as e:
            print(f"Error generating response with Ollama: {e}")
            return "Error: Could not generate a response."
        
    def track_message_frequency(self, chat_message):
        """
        Tracks how frequently a specific message appears in the chat.
        If the message appears more than a certain threshold in a short time, return True to repeat it.
        """
        current_time = datetime.utcnow()

        # Reset message counter periodically
        if current_time - self.last_reset_time > self.message_reset_time:
            self.message_counter.clear()
            self.last_reset_time = current_time

        self.message_counter[chat_message] += 1

        # If the message appears more than 2 times within the reset period, we repeat it
        if self.message_counter[chat_message] > 2:
            return True
        return False

    def adjust_weights_for_popularity(self):
        """
        Adjusts weights for message repetition if certain messages are trending.
        If messages are repeated more than twice, shift weight to mimic those messages.
        """
        for self.chat_message, count in self.message_counter.items():
            if count > 2:
                # If a message is repeated by more than 2 users, adjust the weights to increase the likelihood of repetition
                self.emotes_weight = 0.08
                self.common_phrases_weight = 0.02
                self.ollama_response_weight = 0.9
                return  # No need to adjust further for now

        # Reset to default weights if no specific message is trending
        self.emotes_weight = 0.3
        self.common_phrases_weight = 0.2
        self.ollama_response_weight = 0.50

    def clean_response(self, response_text):
        """
        Cleans the response to remove unnecessary quotes and keep it short and simple.
        """
        # Remove leading and trailing quotes, and other unnecessary formatting
        response_text = response_text.strip('"')
        response_text = response_text.strip("'")
        return response_text

    def log_feedback(self, chat_message, response, is_modified=False):
        """
        Logs the chat messages and responses for future review or feedback analysis.
        """
        feedback_entry = {
            "chat_message": chat_message,
            "response": response,
            "is_modified": is_modified
        }

        try:
            with open(self.feedback_log, "a") as log_file:
                log_file.write(json.dumps(feedback_entry) + "\n")
        except Exception as e:
            print(f"Error logging feedback: {e}")
