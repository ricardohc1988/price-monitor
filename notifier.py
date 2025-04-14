from telegram import Bot
from config_private import TOKEN, MY_CHAT_ID

# Sustituye por tu token real
TELEGRAM_TOKEN = TOKEN
CHAT_ID = MY_CHAT_ID

bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_alert(message, url=None):
    try:
        if url:
            # Use Markdown to send the link
            message = f"{message}\n\n🔗 More Details: [See product]({url})"
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print("✅ Alert sent via Telegram.")
    except Exception as e:
        print(f"❌ Error sending Telegram alert: {e}")