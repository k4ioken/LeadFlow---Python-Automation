# LeadFlow

Comprehensive documentation for the LeadFlow project: purpose, setup, configuration, usage, and impact points.

---

LeadFlow is a Python-based automation tool for managing and nurturing sales leads. It features a secure, web-based admin dashboard built with Streamlit for monitoring live data, filtering leads, and manually triggering outreach campaigns. The system integrates with Google Sheets as its database and sends automated follow-up messages ("nudges") via multiple channels like Telegram and Twilio.

## Features

*   **Web-Based Admin Dashboard:** A rich, interactive UI built with Streamlit to monitor and manage leads.
*   **Secure Authentication:** The dashboard is protected by a login screen, with user credentials managed via environment variables.
*   **Automated Lead Nudges:** A core job (`run_daily_nudge`) automatically sends follow-up messages to leads based on their status and a scheduled follow-up date.
*   **Multi-Channel Notifications:** Out-of-the-box support for sending messages through Telegram and Twilio (WhatsApp).
*   **Google Sheets Integration:** Uses a Google Sheet as a lightweight, accessible database for lead information.
*   **Scheduled & Manual Execution:** The outreach job can be triggered manually from the dashboard or run automatically on a daily schedule using GitHub Actions.
*   **Developer-Friendly:** Includes a Dev Container configuration for a quick and consistent setup in environments like GitHub Codespaces.
*   **Utility Scripts:** A helper script (`get_ids.py`) is provided to easily find Telegram Chat IDs for setting up notifications.

## How It Works

1.  **Data Source:** All lead data is stored and managed in a designated Google Sheet.
2.  **Dashboard (`app.py`):** A Streamlit application provides a secure, real-time view of the Google Sheet data. After logging in, users can view metrics, filter leads by organization or status, and see a live table of records.
3.  **Manual Outreach:** From the dashboard, a user can select a target group of leads and click "Run outreach sequence" to immediately execute the follow-up job for that segment.
4.  **Automated Outreach (`daily_nudge.yml`):** A GitHub Actions workflow runs on a daily schedule (`30 1 * * *` UTC). It sets up the environment, authenticates, and runs the same core `run_daily_nudge` job to process all pending leads that are due for a follow-up.
5.  **Core Logic (`leadflow/jobs.py`):** The `run_daily_nudge` function fetches all records, filters for leads with a "Pending" status and a follow-up date on or before the current day, and uses the `Notifier` to send a pre-defined message.
6.  **Notifications (`leadflow/notifier.py`):** The `Notifier` class handles the logic for sending messages through different APIs (Telegram, Twilio) based on the "Lead Source" specified in the sheet.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/k4ioken/leadflow---python-automation.git
    cd leadflow---python-automation
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS / Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application is configured using environment variables and a Google Cloud service account file.

1.  **Google Service Account:**
    *   Create a Google Cloud service account with permissions for Google Sheets and Google Drive APIs.
    *   Download the JSON key file and save it as `service_account.json` in the root of the project directory.
    *   Share your Google Sheet with the service account's email address (found in the JSON file).

2.  **Environment Variables:**
    Create a `.env` file in the root directory and add the following variables.

    ```env
    # Google Sheet Name
    SHEET_NAME="Your Google Sheet Name"

    # Dashboard Authentication (Choose one method)
    # Method 1: JSON list of users
    LEADFLOW_AUTH_USERS='[{"username": "admin", "password": "secure_password_1"}, {"username": "user2", "password": "secure_password_2"}]'
    # Method 2: Individual user pairs (up to 2 supported)
    LEADFLOW_AUTH_USER_1="admin"
    LEADFLOW_AUTH_PASSWORD_1="secure_password_1"

    # Notification Services
    TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    TWILIO_ACCOUNT_SID="your_twilio_sid"
    TWILIO_AUTH_TOKEN="your_twilio_auth_token"
    TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886" # Your Twilio WhatsApp number
    ```
    If no authentication variables are set, the dashboard will display a setup error and will not load.

## Usage

### Running the Admin Dashboard

To start the local web server and view the dashboard:

```bash
streamlit run app.py
```

Navigate to the local URL provided by Streamlit and log in with the credentials defined in your environment variables.

### Finding Telegram Chat IDs

To set up Telegram notifications, you need the Chat ID of the recipient. Have the user send a `/start` message to your bot first, then run the utility script:

```bash
python get_ids.py
```

This will print the Name, Username, and Chat ID for all users who have recently interacted with your bot.

### Manual Script Execution

You can run the daily nudge job directly from your terminal. This is the same command used by the GitHub Actions workflow.

```bash
python -c "from leadflow.jobs import run_daily_nudge; from dotenv import load_dotenv; load_dotenv(); run_daily_nudge()"
```

## Scheduled Automation with GitHub Actions

The repository includes a GitHub Actions workflow file at `.github/workflows/daily_nudge.yml`. This workflow automates the `run_daily_nudge` job.

*   **Trigger:** It runs on a schedule (daily at 01:30 UTC) and can also be triggered manually from the "Actions" tab in your GitHub repository.
*   **Secrets:** To enable the workflow, you must configure the following secrets in your repository settings (`Settings > Secrets and variables > Actions`):
    *   `GOOGLE_CREDENTIALS_JSON`: The complete JSON content of your `service_account.json` file.
    *   `SHEET_NAME`: The name of your Google Sheet.
    *   `TELEGRAM_BOT_TOKEN`
    *   `TWILIO_ACCOUNT_SID`
    *   `TWILIO_AUTH_TOKEN`
    *   `TWILIO_WHATSAPP_NUMBER`
