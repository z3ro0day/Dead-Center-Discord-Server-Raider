DISWEB Terminal Panel

A pure terminal menu-based tool for managing Discord webhooks and bots.
Built for Linux (tested on Kali), but works on Windows too.

------------------------------------------------------------------------

✨ Features

-   ASCII Art Banner + Colored Menus
-   Webhook Management
    -   Add / Update webhooks
    -   Test webhook connection
    -   Delete saved webhooks
    -   List saved webhooks
    -   Export webhooks (webhooks_backup.json)
    -   Import webhooks
-   Send Messages
    -   Send to a single saved webhook (pick by number)
    -   Send to ALL saved webhooks in parallel
    -   Send to custom (temporary) webhooks in parallel
    -   Optional delay between messages
-   Logs
    -   Stores sent message IDs per webhook
    -   View logs from JSON
-   Bot Management
    -   Send message to channel
    -   Delete last message
    -   Delete all messages
    -   Delete channel
    -   Ban user
    -   Kick user

------------------------------------------------------------------------

📦 Requirements

-   Python 3.8+
-   requests library

Install dependencies: pip install requests

------------------------------------------------------------------------

▶️ Usage

Run the script:

    python3 disweb_terminal.py

On first run, it will auto-create these files: - webhooks.json – saved
webhooks
- logs.json – webhook message logs
- bot_logs.json – bot message logs
- settings.json – basic settings

------------------------------------------------------------------------

📂 File Overview

-   disweb_terminal.py – the main program
-   webhooks.json – stores your saved webhooks
-   webhooks_backup.json – used for export/import
-   logs.json – stores webhook message IDs
-   bot_logs.json – stores bot message IDs

------------------------------------------------------------------------

⚡ Example

Add a Webhook: 1. Open Manage Webhooks 2. Choose Add/Update 3. Enter: -
Webhook name (local label) - Webhook URL - Username to display

Send to All Webhooks: 1. Open Send Messages 2. Choose Send to ALL Saved
Webhooks (parallel) 3. Enter message and options

------------------------------------------------------------------------

❗ Notes

-   This script is for personal/admin use only.
-   Be careful with spamming – Discord may rate-limit requests.
-   Default delay is 0s (fastest possible). Increase if needed.

------------------------------------------------------------------------

✅ License

Free to use and modify.
