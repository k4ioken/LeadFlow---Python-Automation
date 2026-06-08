import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from twilio.rest import Client
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file automatically
load_dotenv()

class Notifier:
    def __init__(self):
        # 1. Telegram Credentials
        self.telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        
        # 2. Twilio Sandbox Credentials (For future WhatsApp testing)
        self.twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")
        
        if self.twilio_sid and self.twilio_token:
            self.twilio_client = Client(self.twilio_sid, self.twilio_token)
            
        # 3. Official WhatsApp Business API (WABA) Credentials
        self.waba_token = os.environ.get("WABA_ACCESS_TOKEN")
        self.waba_phone_id = os.environ.get("WABA_PHONE_NUMBER_ID")

    def send_telegram(self, chat_id, message):
        """Sends a message via Telegram Bot API."""
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
        """Sends a message via Twilio Sandbox. Expects number format +919876543210"""
        if not self.twilio_sid:
            print("Twilio credentials missing in .env")
            return False
            
        try:
            formatted_number = f"whatsapp:{phone_number}" if not str(phone_number).startswith("whatsapp:") else phone_number
            msg = self.twilio_client.messages.create(
                from_=self.twilio_number, 
                body=message, 
                to=formatted_number
            )
            return True
        except Exception as e:
            print(f"Twilio Error: {str(e)}")
            return False

    def send_official_whatsapp(self, phone_number, message):
        """Placeholder for production Meta Cloud API."""
        print("Official WABA endpoint hit. Need production keys to send.")
        return False

def run_daily_nudge():
    # --- Authenticate with Google Sheets ---
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    g_client = gspread.authorize(creds)
    sheetname = os.environ.get("SHEET_NAME")
    # Open the sheet (Make sure this exactly matches your Google Sheet name)
    sheet = g_client.open(sheetname).sheet1

    records = sheet.get_all_records()
    today = datetime.now().strftime("%Y-%m-%d")
    notifier = Notifier()

    print(f"Running automated outreach check for {today}...\n")

    # enumerate starting at 2 because row 1 is the header row in Google Sheets
    for i, row in enumerate(records, start=2):
        # .strip() prevents errors if you accidentally leave a space in the sheet cells
        status = str(row.get("Status", "")).strip()
        follow_up_date = str(row.get("Follow-up Date", "")).strip()
        
        # Updated to use your new column names
        # Updated to use exact matching capitalization
        platform = str(row.get("Lead Source", "")).strip().lower()
        contact_id = str(row.get("Lead Contact ID", "")).strip()
        
        # Clean the data in case Google Sheets introduces a float decimal
        if contact_id.endswith(".0"):
            contact_id = contact_id[:-2]
            
        lead_name = str(row.get("Lead Name", "")).strip()
        organization = str(row.get("Organization", "")).strip()

        if status == "Pending" and follow_up_date == today:
            
            # Fallback in case the organization cell is empty in the sheet
            display_org = organization if organization else "our team"
            
            # Dynamic message copy
            message_body = (
                f"Hi {lead_name}, this is an automated follow-up from {display_org}. \n\n"
                f"We noticed your profile is still pending. Are you still looking to secure your spot "
                f"for the upcoming batch? Let us know how we can help!"
            )
            
            success = False
            
            # Route the notification based on Lead Source mapping
            if platform == "telegram":
                success = notifier.send_telegram(contact_id, message_body)
            elif platform == "twilio":
                success = notifier.send_twilio_whatsapp(contact_id, message_body)
            elif platform == "waba":
                success = notifier.send_official_whatsapp(contact_id, message_body)
            else:
                print(f"Unknown platform '{platform}' for lead: {lead_name}")
            
            # Update the sheet if successful
            if success:
                print(f"Nudge sent via {platform} to {lead_name} on behalf of {display_org}.")
                
                # Status remains Column B (index 2) as long as Lead Name is Column A
                sheet.update_cell(i, 2, "Nudged") 

if __name__ == "__main__":
    run_daily_nudge()