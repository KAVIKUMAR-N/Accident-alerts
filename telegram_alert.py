import requests
import config

def send_alert(message, image_path=None):

    if image_path:

        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"

        files = {
            "photo": open(image_path, "rb")
        }

        data = {
            "chat_id": config.CHAT_ID,
            "caption": message
        }

        requests.post(url, data=data, files=files)

    else:

        url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendMessage"

        data = {
            "chat_id": config.CHAT_ID,
            "text": message
        }

        requests.post(url, data=data)