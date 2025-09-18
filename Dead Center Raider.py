#!/usr/bin/env python3
import os, json, time, requests, threading

# ---------------- Colors ----------------
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# ---------------- Files ----------------
WEBHOOK_FILE = "webhooks.json"
WEBHOOK_BACKUP = "webhooks_backup.json"
LOG_FILE = "logs.json"
BOT_LOG_FILE = "bot_logs.json"
SETTINGS_FILE = "settings.json"

# ---------------- Helpers ----------------
def load_json(path, default):
    if not os.path.exists(path):
        save_json(path, default)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

# Initialize files on first run
webhooks = load_json(WEBHOOK_FILE, {})
logs = load_json(LOG_FILE, {})
bot_logs = load_json(BOT_LOG_FILE, {})
settings = load_json(SETTINGS_FILE, {"first_run": True})

# ---------------- Banner ----------------
def banner():
    print(BLUE + """
██████╗ ███████╗ █████╗ ██████╗      ██████╗███████╗███╗   ██╗████████╗███████╗██████╗     ██████╗  █████╗ ██╗██████╗ ███████╗██████╗ 
██╔══██╗██╔════╝██╔══██╗██╔══██╗    ██╔════╝██╔════╝████╗  ██║╚══██╔══╝██╔════╝██╔══██╗    ██╔══██╗██╔══██╗██║██╔══██╗██╔════╝██╔══██╗
██║  ██║█████╗  ███████║██║  ██║    ██║     █████╗  ██╔██╗ ██║   ██║   █████╗  ██████╔╝    ██████╔╝███████║██║██║  ██║█████╗  ██████╔╝
██║  ██║██╔══╝  ██╔══██║██║  ██║    ██║     ██╔══╝  ██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗    ██╔══██╗██╔══██║██║██║  ██║██╔══╝  ██╔══██╗
██████╔╝███████╗██║  ██║██████╔╝    ╚██████╗███████╗██║ ╚████║   ██║   ███████╗██║  ██║    ██║  ██║██║  ██║██║██████╔╝███████╗██║  ██║
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═════╝      ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
""" + RESET)

# ---------------- Webhook Helpers ----------------
def test_webhook(url: str) -> bool:
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 200
    except Exception:
        return False

def _append_wait_param(url: str) -> str:
    return url + ("&wait=true" if "?" in url else "?wait=true")

def send_webhook_message(url: str, username: str, content: str):
    payload = {"username": username, "content": content}
    try:
        r = requests.post(_append_wait_param(url), json=payload, timeout=20)
        if r.status_code in (200, 201) and r.headers.get("Content-Type","").startswith("application/json"):
            return r.json()
        elif r.status_code == 204:
            return {}
        elif r.status_code == 429:
            retry = float(r.json().get("retry_after", 1.0))
            time.sleep(retry)
            return send_webhook_message(url, username, content)
        else:
            return None
    except Exception:
        return None

# ---------------- Bot Helpers ----------------
API = "https://discord.com/api/v10"

def bot_headers(token: str):
    return {"Authorization": f"Bot {token}", "Content-Type": "application/json"}

def bot_send_message(token: str, channel_id: str, content: str):
    try:
        r = requests.post(f"{API}/channels/{channel_id}/messages",
                          headers=bot_headers(token),
                          json={"content": content},
                          timeout=20)
        if r.status_code in (200, 201):
            return r.json()
        elif r.status_code == 429:
            time.sleep(float(r.json().get("retry_after", 1.0)))
            return bot_send_message(token, channel_id, content)
        else:
            return None
    except Exception:
        return None

def bot_delete_message(token: str, channel_id: str, message_id: str) -> bool:
    try:
        r = requests.delete(f"{API}/channels/{channel_id}/messages/{message_id}",
                            headers=bot_headers(token), timeout=15)
        return r.status_code in (200, 204, 404)
    except Exception:
        return False

def bot_delete_channel(token: str, channel_id: str) -> bool:
    try:
        r = requests.delete(f"{API}/channels/{channel_id}",
                            headers=bot_headers(token), timeout=20)
        return r.status_code in (200, 204)
    except Exception:
        return False

def bot_ban_user(token: str, guild_id: str, user_id: str) -> bool:
    try:
        r = requests.put(f"{API}/guilds/{guild_id}/bans/{user_id}",
                         headers=bot_headers(token), json={}, timeout=20)
        return r.status_code in (200, 201, 204)
    except Exception:
        return False

def bot_kick_user(token: str, guild_id: str, user_id: str) -> bool:
    try:
        r = requests.delete(f"{API}/guilds/{guild_id}/members/{user_id}",
                            headers=bot_headers(token), timeout=20)
        return r.status_code in (200, 204)
    except Exception:
        return False

# ---------------- Menus ----------------
def manage_webhooks_menu():
    while True:
        clear()
        banner()
        print(YELLOW + "\n=== Manage Webhooks ===" + RESET)
        print("1. Add/Update Webhook")
        print("2. Test Webhook")
        print("3. Delete Local Webhook")
        print("4. List Webhooks")
        print("5. Export Webhooks")
        print("6. Import Webhooks")
        print("7. Back")
        choice = input("> ")

        if choice == "1":
            name = input("Name: ").strip()
            url = input("Webhook URL: ").strip()
            user = input("Username: ").strip() or "DISWEB WEBHOOK"
            if not test_webhook(url):
                print(RED + "[ERROR] Webhook test failed." + RESET)
            else:
                webhooks[name] = {"url": url, "user": user}
                save_json(WEBHOOK_FILE, webhooks)
                print(GREEN + "[OK] Webhook saved." + RESET)
            input("Press Enter to continue...")

        elif choice == "2":
            name = input("Webhook Name: ").strip()
            if name in webhooks:
                ok = test_webhook(webhooks[name]["url"])
                print(GREEN + "[OK]" + RESET if ok else RED + "[FAILED]" + RESET)
            else:
                print(RED + "[ERROR] Not found." + RESET)
            input("Press Enter to continue...")

        elif choice == "3":
            name = input("Webhook Name: ").strip()
            if webhooks.pop(name, None):
                save_json(WEBHOOK_FILE, webhooks)
                print(GREEN + "[OK] Deleted locally." + RESET)
            else:
                print(RED + "[ERROR] Not found." + RESET)
            input("Press Enter to continue...")

        elif choice == "4":
            print(json.dumps(webhooks, indent=2))
            input("Press Enter to continue...")

        elif choice == "5":  # Export
            save_json(WEBHOOK_BACKUP, webhooks)
            print(GREEN + f"[OK] Exported to {WEBHOOK_BACKUP}" + RESET)
            input("Press Enter to continue...")

        elif choice == "6":  # Import
            imported = load_json(WEBHOOK_BACKUP, {})
            if imported:
                webhooks.update(imported)
                save_json(WEBHOOK_FILE, webhooks)
                print(GREEN + "[OK] Webhooks imported." + RESET)
            else:
                print(RED + "[ERROR] No backup file found or empty." + RESET)
            input("Press Enter to continue...")

        elif choice == "7":
            break

def send_messages_menu():
    while True:
        clear()
        banner()
        print(YELLOW + "\n=== Send Messages ===" + RESET)
        print("1. Send to Saved Webhook")
        print("2. Send to ALL Saved Webhooks (parallel)")
        print("3. Send to Custom Webhooks (temporary, parallel)")
        print("4. Back")
        choice = input("> ")

        if choice == "1":
            if not webhooks:
                print(RED + "[ERROR] No saved webhooks." + RESET)
                input("Press Enter to continue...")
                continue

            print(BLUE + "\nSaved Webhooks:" + RESET)
            for idx, (name, data) in enumerate(webhooks.items(), start=1):
                print(f"{idx}. {name} ({data['url'][:40]}...)")

            try:
                selection = int(input("Select webhook number: "))
                name = list(webhooks.keys())[selection - 1]
            except (ValueError, IndexError):
                print(RED + "[ERROR] Invalid selection." + RESET)
                input("Press Enter to continue...")
                continue

            content = input("Message: ").strip()
            count = int(input("Count: ") or "1")
            delay = float(input("Delay (s, default=0): ") or "0")

            sent = 0
            for i in range(count):
                resp = send_webhook_message(webhooks[name]["url"], webhooks[name]["user"], content)
                if resp:
                    logs.setdefault(name, []).append(resp.get("id"))
                    save_json(LOG_FILE, logs)
                    sent += 1
                    print(GREEN + f"[OK] Sent {sent}/{count}" + RESET)
                if delay > 0:
                    time.sleep(delay)
            print(BLUE + "[DONE] Finished sending." + RESET)
            input("Press Enter to continue...")

        elif choice == "2":
            if not webhooks:
                print(RED + "[ERROR] No saved webhooks." + RESET)
                input("Press Enter to continue...")
                continue

            content = input("Message: ").strip()
            count = int(input("Count: ") or "1")
            delay = float(input("Delay (s, default=0): ") or "0")

            def worker(name, data):
                sent = 0
                for i in range(count):
                    resp = send_webhook_message(data["url"], data["user"], content)
                    if resp:
                        logs.setdefault(name, []).append(resp.get("id"))
                        save_json(LOG_FILE, logs)
                        sent += 1
                        print(GREEN + f"[{name}] Sent {sent}/{count}" + RESET)
                    if delay > 0:
                        time.sleep(delay)

            threads = []
            for name, data in webhooks.items():
                t = threading.Thread(target=worker, args=(name, data))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            print(BLUE + "[DONE] Finished sending to ALL webhooks." + RESET)
            input("Press Enter to continue...")

        elif choice == "3":
            urls = []
            print(BLUE + "Enter webhook URLs (one per line). Leave blank when done." + RESET)
            while True:
                url = input("Webhook URL: ").strip()
                if not url:
                    break
                urls.append(url)

            if not urls:
                print(RED + "[ERROR] No webhooks entered." + RESET)
                input("Press Enter to continue...")
                continue

            username = input("Username to show: ").strip() or "DISWEB CUSTOM"
            content = input("Message: ").strip()
            count = int(input("Count: ") or "1")
            delay = float(input("Delay (s, default=0): ") or "0")

            def worker(url):
                sent = 0
                for i in range(count):
                    resp = send_webhook_message(url, username, content)
                    if resp:
                        sent += 1
                        print(GREEN + f"[{url[:30]}...] Sent {sent}/{count}" + RESET)
                    if delay > 0:
                        time.sleep(delay)

            threads = []
            for url in urls:
                t = threading.Thread(target=worker, args=(url,))
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            print(BLUE + "[DONE] Finished sending to custom webhooks." + RESET)
            input("Press Enter to continue...")

        elif choice == "4":
            break

# ---------------- Other Menus ----------------
def logs_menu():
    while True:
        clear()
        banner()
        print(YELLOW + "\n=== Logs ===" + RESET)
        print("1. View Logs")
        print("2. Back")
        choice = input("> ")
        if choice == "1":
            print(json.dumps(logs, indent=2))
            input("Press Enter to continue...")
        elif choice == "2":
            break

def bot_management_menu():
    while True:
        clear()
        banner()
        print(YELLOW + "\n=== Bot Management ===" + RESET)
        print("1. Send Message")
        print("2. Delete Last Message")
        print("3. Delete All Messages")
        print("4. Delete Channel")
        print("5. Ban User")
        print("6. Kick User")
        print("7. Back")
        choice = input("> ")

        if choice == "1":
            token = input("Bot Token: ").strip()
            channel = input("Channel ID: ").strip()
            content = input("Message: ").strip()
            count = int(input("Count: ") or "1")
            delay = float(input("Delay (s): ") or "0")
            sent = 0
            for i in range(count):
                resp = bot_send_message(token, channel, content)
                if resp:
                    bot_logs.setdefault(channel, []).append(resp["id"])
                    save_json(BOT_LOG_FILE, bot_logs)
                    sent += 1
                    print(GREEN + f"[OK] Sent {sent}/{count}" + RESET)
                if delay > 0:
                    time.sleep(delay)
            print(BLUE + "[DONE] Finished sending." + RESET)
            input("Press Enter to continue...")

        elif choice == "2":
            token = input("Bot Token: ").strip()
            channel = input("Channel ID: ").strip()
            if channel in bot_logs and bot_logs[channel]:
                mid = bot_logs[channel].pop()
                ok = bot_delete_message(token, channel, mid)
                save_json(BOT_LOG_FILE, bot_logs)
                print(GREEN + "[OK] Deleted." + RESET if ok else RED + "[FAILED]" + RESET)
            else:
                print(RED + "[ERROR] No logged messages." + RESET)
            input("Press Enter to continue...")

        elif choice == "3":
            token = input("Bot Token: ").strip()
            channel = input("Channel ID: ").strip()
            if channel in bot_logs and bot_logs[channel]:
                for mid in list(bot_logs[channel]):
                    bot_delete_message(token, channel, mid)
                bot_logs[channel] = []
                save_json(BOT_LOG_FILE, bot_logs)
                print(GREEN + "[OK] All messages deleted." + RESET)
            else:
                print(RED + "[ERROR] No logged messages." + RESET)
            input("Press Enter to continue...")

        elif choice == "4":
            token = input("Bot Token: ").strip()
            channel = input("Channel ID: ").strip()
            ok = bot_delete_channel(token, channel)
            print(GREEN + "[OK] Channel deleted." + RESET if ok else RED + "[FAILED]" + RESET)
            input("Press Enter to continue...")

        elif choice == "5":
            token = input("Bot Token: ").strip()
            guild = input("Guild ID: ").strip()
            user = input("User ID: ").strip()
            ok = bot_ban_user(token, guild, user)
            print(GREEN + "[OK] User banned." + RESET if ok else RED + "[FAILED]" + RESET)
            input("Press Enter to continue...")

        elif choice == "6":
            token = input("Bot Token: ").strip()
            guild = input("Guild ID: ").strip()
            user = input("User ID: ").strip()
            ok = bot_kick_user(token, guild, user)
            print(GREEN + "[OK] User kicked." + RESET if ok else RED + "[FAILED]" + RESET)
            input("Press Enter to continue...")

        elif choice == "7":
            break

# ---------------- Main ----------------
def main():
    while True:
        clear()
        banner()
        print(YELLOW + "\n=== Main Menu ===" + RESET)
        print("1. Manage Webhooks")
        print("2. Send Messages")
        print("3. Logs")
        print("4. Bot Management")
        print("5. Exit")
        choice = input("> ")
        if choice == "1":
            manage_webhooks_menu()
        elif choice == "2":
            send_messages_menu()
        elif choice == "3":
            logs_menu()
        elif choice == "4":
            bot_management_menu()
        elif choice == "5":
            print(GREEN + "[EXIT] Goodbye." + RESET)
            break

if __name__ == "__main__":
    main()
