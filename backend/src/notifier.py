"""
notifier.py — Telegram message dispatch for flood alerts.
Email support skipped per user request.
"""
import os
import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"

def _get_token() -> str | None:
    return os.environ.get("TELEGRAM_BOT_TOKEN")

def format_telegram_alert(alert: dict) -> str:
    """Format a structured alert dict into a Telegram-friendly message."""
    risk = alert.get("risk_level", "Unknown")
    district = alert.get("district", "Unknown")
    locality = alert.get("locality", "district_wide")
    prob = alert.get("flood_probability", 0)
    date = alert.get("predicted_date", "N/A")
    factors = alert.get("main_factors", [])
    
    emoji = "🔴" if risk == "High" else "🟡" if risk == "Medium" else "🟢"
    
    msg = f"""{emoji} *FloodPulse Alert*
    
📍 *{district}* — {locality}
📅 Date: {date}
⚠️ Risk Level: *{risk}*
📊 Probability: {round(prob * 100, 1)}%

*Contributing Factors:*
"""
    for f in factors[:5]:
        msg += f"• {f}\n"
    
    msg += "\n_Stay safe. Monitor KSNDMC advisories._"
    return msg

def send_telegram(chat_id: str, message: str) -> bool:
    """Send a message to a Telegram chat ID."""
    token = _get_token()
    if not token:
        print("WARNING: TELEGRAM_BOT_TOKEN not set. Skipping send.")
        return False
    
    url = TELEGRAM_API.format(token=token)
    try:
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False

def dispatch_alert(alert: dict, subscribers: list) -> int:
    """Dispatch alert to all matching subscribers. Returns count sent."""
    sent = 0
    message = format_telegram_alert(alert)
    
    for sub in subscribers:
        if sub["contact_method"] == "telegram":
            if send_telegram(sub["contact_value"], message):
                sent += 1
    
    return sent
