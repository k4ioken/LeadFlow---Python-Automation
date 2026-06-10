import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv
import streamlit as st  # Added for cloud secrets fallback

load_dotenv()

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
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Telegram Error: {str(e)}")
            return False

    def send_twilio_whatsapp(self, phone_number, message):
        if not self.twilio_sid:
            return False
        try:
            formatted_number = f"whatsapp:{phone_number}" if not str(phone_number).startswith("whatsapp:") else phone_number
            self.twilio_client.messages.create(
                from_=self.twilio_number, 
                body=message, 
                to=formatted_number
            )
            return True
        except Exception as e:
            print(f"Twilio Error: {str(e)}")
            return False

    def send_official_whatsapp(self, phone_number, message):
        print("Official WABA endpoint hit. Need production keys to send.")
        return False

def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
    if os.path.exists(secrets_path) and "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)

    return gspread.authorize(creds)
    """Handles authentication for both Local (.json file) and Cloud (Streamlit Secrets)"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Check if running on Streamlit Cloud with secrets configured
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    else:
        # Local fallback using your physical file
        creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
        
    return gspread.authorize(creds)

def run_daily_nudge(target_org="All Pending"):
    """Executes outreach and returns logs/stats back to the Streamlit UI"""
    g_client = get_gspread_client()
    sheetname = os.environ.get("SHEET_NAME")
    sheet = g_client.open(sheetname).sheet1

    records = sheet.get_all_records()
    today = datetime.now().strftime("%Y-%m-%d")
    notifier = Notifier()
    
    logs = []
    sent_count = 0

    for i, row in enumerate(records, start=2):
        status = str(row.get("Status", "")).strip()
        follow_up_date = str(row.get("Follow-up Date", "")).strip()
        platform = str(row.get("Lead Source", "")).strip().lower()
        contact_id = str(row.get("Lead Contact ID", "")).strip()
        lead_name = str(row.get("Lead Name", "")).strip()
        organization = str(row.get("Organization", "")).strip()

        if contact_id.endswith(".0"):
            contact_id = contact_id[:-2]

        # Filter by organization selected in UI (or process all if 'All Pending' is chosen)
        org_matches = (target_org == "All Pending") or (organization.lower() == target_org.lower())

        if status == "Pending" and follow_up_date <= today and org_matches:
            display_org = organization if organization else "our team"
            message_body = (
                f"Hi {lead_name}, this is an automated follow-up from {display_org}. \n\n"
                f"We noticed your profile is still pending. Are you still looking to secure your spot "
                f"for the upcoming batch? Let us know how we can help!"
            )
            
            success = False
            if platform == "telegram":
                success = notifier.send_telegram(contact_id, message_body)
            elif platform == "twilio":
                success = notifier.send_twilio_whatsapp(contact_id, message_body)
            elif platform == "waba":
                success = notifier.send_official_whatsapp(contact_id, message_body)

            if success:
                sheet.update_cell(i, 2, "Nudged") 
                logs.append(f"Nudge sent via {platform} to {lead_name} ({organization})")
                sent_count += 1
            else:
                logs.append(f"Failed to send to {lead_name} via {platform}")

    return sent_count, logs

if __name__ == "__main__":
    # Keeps terminal execution working perfectly if run manually
    run_daily_nudge()