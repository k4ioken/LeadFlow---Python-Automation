import os
import requests
from twilio.rest import Client

class Notifier:
    def __init__(self):
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")

        if self.twilio_sid and self.twilio_token:
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)

        self.waba_token = os.environ.get("WABA_ACCESS_TOKEN")
        self.waba_phone_id = os.environ.get("WABA_PHONE_NUMBER_ID")

    def send_telegram(self, chat_id, message):
        if not self.telegram_token:
            return False
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            resp = requests.post(url, json=payload)
            resp.raise_for_status()
            return True
        except Exception:
            return False

    def send_twilio_whatsapp(self, phone_number, message):
        if not (self.twilio_sid and self.twilio_token):
            return False
        try:
            formatted_number = f"whatsapp:{phone_number}" if not str(phone_number).startswith("whatsapp:") else phone_number
            self.twilio_client.messages.create(
                from_=self.twilio_number,
                body=message,
                to=formatted_number
            )
            return True
        except Exception:
            return False

    def send_official_whatsapp(self, phone_number, message):
        # Placeholder for WABA integration
        return False
