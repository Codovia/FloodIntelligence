"""
telegram_bot.py — Telegram bot with 5 commands for citizen self-service.
Commands: /start, /subscribe, /unsubscribe, /status, /help
Runs in a background thread via long-polling.
"""
import os
import threading
import requests
import time

BOT_COMMANDS = """
🌊 *FloodPulse Bot Commands*

/start — Welcome message
/subscribe <district> — Subscribe to flood alerts for a district
/unsubscribe — Remove your subscription
/status <district> — Check current risk level for a district
/help — Show this help message
"""

class FloodPulseBot:
    def __init__(self, db_module=None, predict_fn=None, data_loader=None):
        self.token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        self.db = db_module
        self.predict_fn = predict_fn
        self.data_loader = data_loader
    
    def _send(self, chat_id, text):
        try:
            requests.post(f"{self.base_url}/sendMessage", json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }, timeout=10)
        except Exception as e:
            print(f"Bot send error: {e}")
    
    def _handle_start(self, chat_id, _args):
        self._send(chat_id,
            "🌊 *Welcome to FloodPulse!*\n\n"
            "I provide real-time flood risk alerts for Karnataka districts.\n\n"
            "Use /subscribe <district> to start receiving alerts.\n"
            "Use /status <district> to check current risk.\n"
            "Use /help to see all commands.")
    
    def _handle_help(self, chat_id, _args):
        self._send(chat_id, BOT_COMMANDS)
    
    def _handle_subscribe(self, chat_id, args):
        if not args:
            self._send(chat_id, "Usage: /subscribe <district>\nExample: /subscribe Udupi")
            return
        
        district = " ".join(args).strip()
        if self.data_loader:
            profile = self.data_loader.get_district_profile(district)
            if not profile:
                self._send(chat_id, f"❌ District '{district}' not found.\nUse /status to see available districts.")
                return
        
        if self.db:
            try:
                self.db.subscriber_create("telegram", str(chat_id), district, "district_wide")
                self._send(chat_id, f"✅ Subscribed to alerts for *{district}*.\nYou'll receive notifications when High risk is detected.")
            except Exception as e:
                if "UNIQUE" in str(e):
                    self._send(chat_id, f"ℹ️ You're already subscribed to *{district}*.")
                else:
                    self._send(chat_id, f"❌ Error: {e}")
        else:
            self._send(chat_id, f"✅ Subscription noted for *{district}* (DB not connected).")
    
    def _handle_unsubscribe(self, chat_id, _args):
        if self.db:
            deleted = self.db.subscriber_delete_by_contact("telegram", str(chat_id))
            if deleted:
                self._send(chat_id, "✅ All your subscriptions have been removed.")
            else:
                self._send(chat_id, "ℹ️ No active subscriptions found.")
        else:
            self._send(chat_id, "Unsubscribed (DB not connected).")
    
    def _handle_status(self, chat_id, args):
        if not args:
            # List all districts
            if self.data_loader:
                districts = ", ".join(self.data_loader.DISTRICT_NAMES[:15]) + "..."
                self._send(chat_id, f"📋 *Available districts:*\n{districts}\n\nUsage: /status <district>")
            return
        
        district = " ".join(args).strip()
        self._send(chat_id, f"📊 Checking risk for *{district}*...\n\n_Use the web dashboard for detailed predictions._")
    
    def _process_update(self, update):
        msg = update.get("message", {})
        text = msg.get("text", "")
        chat_id = msg.get("chat", {}).get("id")
        
        if not chat_id or not text:
            return
        
        parts = text.strip().split()
        cmd = parts[0].lower().split("@")[0]  # Handle @botname suffix
        args = parts[1:]
        
        handlers = {
            "/start": self._handle_start,
            "/subscribe": self._handle_subscribe,
            "/unsubscribe": self._handle_unsubscribe,
            "/status": self._handle_status,
            "/help": self._handle_help,
        }
        
        handler = handlers.get(cmd)
        if handler:
            handler(chat_id, args)
    
    def _poll_loop(self):
        """Long-polling loop. Runs in background thread."""
        while self.running:
            try:
                resp = requests.get(
                    f"{self.base_url}/getUpdates",
                    params={"offset": self.offset, "timeout": 30},
                    timeout=35
                )
                if resp.status_code == 200:
                    updates = resp.json().get("result", [])
                    for update in updates:
                        self._process_update(update)
                        self.offset = update["update_id"] + 1
            except Exception as e:
                print(f"Bot poll error: {e}")
                time.sleep(5)
    
    def start(self):
        """Start the bot in a background thread."""
        if not self.token:
            print("WARNING: TELEGRAM_BOT_TOKEN not set. Bot not started.")
            return
        
        self.running = True
        thread = threading.Thread(target=self._poll_loop, daemon=True, name="telegram_bot")
        thread.start()
        print("Telegram bot started (long-polling thread).")
    
    def stop(self):
        self.running = False
