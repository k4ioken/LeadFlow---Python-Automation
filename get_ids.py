import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") 

def fetch_chat_ids():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("ok"):
            print("API Error: Failed to fetch updates.")
            return

        results = data.get("result", [])
        if not results:
            print("No recent messages found. Have your friends send /start to your bot first.")
            return

        print("\n=== Telegram Chat IDs ===")
        # Use a set to avoid printing the same person multiple times
        seen_ids = set() 
        
        for update in results:
            message = update.get("message")
            if message:
                chat = message.get("chat")
                chat_id = chat.get("id")
                first_name = chat.get("first_name", "Unknown")
                username = chat.get("username", "No_Username")
                
                if chat_id not in seen_ids:
                    print(f"Name: {first_name} | Username: @{username} | ID: {chat_id}")
                    seen_ids.add(chat_id)
                    
        print("=========================\n")
        
    except Exception as e:
        print(f"Execution Error: {str(e)}")

if __name__ == "__main__":
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set.")
    else:
        fetch_chat_ids()