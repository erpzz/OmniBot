# Kick Chatbot - README

This is my Kick Chatbot project. It’s a bot that connects to Kick stream chats, reads messages in real-time, and responds using AI. It’s simple to set up and works great for streamers who want a more engaging chat.

---

## How It Works

Here’s the gist:  

- **`main.py`**: Runs the whole thing.  
- **`sockconnect.py`**: Connects to the Kick chat through websockets.  
- **`chatforge.py`**: Processes messages and generates replies using AI.  
- **`chat_database.py`**: Saves chat logs in an SQLite database.  
- **`channel_scraper.py`**: Grabs channel info so the bot connects to the right stream.  

Everything’s designed to be lightweight and easy to customize.

---

## Requirements

You’ll need:  

- **Python 3.8+**  
- Libraries from `requirements.txt`:

```plaintext
websockets==10.3
requests==2.31.0
ollama==1.2.0
sqlite3==3.36.0
```

---

## Setup Instructions

### Clone the Repo

```bash
git clone https://github.com/yourusername/kick-chatbot.git
cd kick-chatbot
```

### Set Up Virtual Env

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Bot

```bash
python main.py
```

That’s it! The bot connects to your Kick channel and starts responding to chat messages.

---

## Quick Tips

- **Edit Responses**: Tweak them in `chatforge.py` to make the bot more personal.  
- **Logs & Data**: Chat logs are saved in `chatdb/`.  
- **Debugging**: If something breaks, check the logs in the terminal.  

---

## Questions or Suggestions?

If you run into issues or have ideas to make this better, let me know. You can email me at: eneftpaiz@gmail.com for inquiries regarding this project or if you'd like to discuss future endeavors.
