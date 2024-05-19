import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TELEGRAM_API_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

UPDATE_URL = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/getUpdates"


def get_bot_updates():
    response = requests.get(UPDATE_URL)
    return response.json()


def get_chat_id(telegram_username):
    response = requests.get(UPDATE_URL)
    data = response.json()
    chat_id = None
    for result in data["result"]:
        username = result["message"]["from"].get("username")
        if username == telegram_username:
            chat_id = result["message"]["chat"]["id"]
            break
    return chat_id


def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TELEGRAM_API_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()
