import os
import requests
import json
import time

# User Provided Token
TOKEN = "8552903618:AAHdUi9BDmJCO7lC7MhmX6BfsflwqX2DqlU"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

print("-" * 40)
print(f"🔄 Connecting to Bot: @AlphaQuantopology_bot")
print("-" * 40)

def test_connection():
    try:
        resp = requests.get(f"{API_URL}/getMe", timeout=10)
        data = resp.json()
        
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"✅ Auth SUCCESS!")
            print(f"🤖 ID: {bot_info.get('id')}")
            print(f"🤖 Name: {bot_info.get('first_name')}")
            print(f"🤖 Username: @{bot_info.get('username')}")
            return True
        else:
            print(f"❌ Auth FAILED: {data.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Connection ERROR: {str(e)}")
        return False

def get_chat_id():
    print("\n🔍 Scanning for Chat ID (checking last messages)...")
    try:
        # Get updates (messages sent to bot)
        resp = requests.get(f"{API_URL}/getUpdates", timeout=10)
        data = resp.json()
        
        if not data.get("ok"):
            print(f"❌ Failed to get updates: {data}")
            return None

        results = data.get("result", [])
        if not results:
            print("⚠️ No messages found. Please send '/start' to the bot now!")
            # Wait loop?
            for i in range(5): 
                print(f"⏳ Waiting for message... ({5-i})")
                time.sleep(2)
                resp = requests.get(f"{API_URL}/getUpdates", timeout=10)
                results = resp.json().get("result", [])
                if results:
                    break
        
        if results:
            last_msg = results[-1]
            chat = last_msg.get("message", {}).get("chat", {})
            chat_id = chat.get("id")
            username = chat.get("username", "Unknown")
            print(f"\n✅ FOUND CHAT ID: {chat_id}")
            print(f"👤 User: @{username}")
            print(f"\n👉 Add this to your .env:\nTELEGRAM_CHAT_ID={chat_id}")
            return chat_id
        else:
             print("\n❌ Still no messages found.")
             print("👉 ACTION REQUIRED: Send '/start' to @AlphaQuantopology_bot on Telegram.")
             return None

    except Exception as e:
        print(f"❌ Error fetching updates: {str(e)}")
        return None

if __name__ == "__main__":
    if test_connection():
        get_chat_id()
    print("-" * 40)

