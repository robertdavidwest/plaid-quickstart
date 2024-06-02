import os
import requests


def get_bot_updates(telegram_api_token):
    update_url = f"https://api.telegram.org/bot{telegram_api_token}/getUpdates"
    response = requests.get(update_url)
    return response.json()


def get_chat_id(telegram_username, telegram_api_token):
    update_url = f"https://api.telegram.org/bot{telegram_api_token}/getUpdates"
    response = requests.get(update_url)
    data = response.json()
    chat_id = None
    for result in data["result"]:
        username = result["message"]["from"].get("username")
        if username == telegram_username:
            chat_id = result["message"]["chat"]["id"]
            break
    return chat_id


def send_message(chat_id, message, telegram_api_token):
    url = f"https://api.telegram.org/bot{telegram_api_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()
