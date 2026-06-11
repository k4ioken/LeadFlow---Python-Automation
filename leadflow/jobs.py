import os
from datetime import datetime
from .auth import get_gspread_client
from .notifier import Notifier

def run_daily_nudge(target_org="All Pending"):
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

        org_matches = (target_org == "All Pending") or (organization.lower() == target_org.lower())

        if status == "Pending" and follow_up_date <= today and org_matches:
            display_org = organization if organization else "our team"
            message_body = (
                f"Hi {lead_name}, this is an automated follow-up from {display_org}.\n\n"
                f"We noticed your profile is still pending. Are you still looking to secure your spot?"
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
