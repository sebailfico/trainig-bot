import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from collections import defaultdict
import sys

DATA_FILE = "training_data.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def get_display_name(user):
    return user.username or user.full_name or str(user.id)

async def trained(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    name = get_display_name(user)

    data = load_data()
    data[user_id] = {
        "count": data.get(user_id, {}).get("count", 0) + 1,
        "name": name
    }
    save_data(data)

    await update.message.reply_text(f"✅ {name}, you've trained {data[user_id]['count']} times!")

async def progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    name = get_display_name(user)

    data = load_data()
    count = data.get(user_id, {}).get("count", 0)

    await update.message.reply_text(f"📈 {name}, you've trained {count} times.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1]['count'], reverse=True)

    if not sorted_users:
        await update.message.reply_text("No one has logged training yet.")
        return

    message = "🏆 *Training Leaderboard:*\n\n"
    for idx, (user_id, info) in enumerate(sorted_users, start=1):
        message += f"{idx}. {info['name']} — {info['count']} times\n"

    await update.message.reply_markdown(message)

async def main():
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("❌ Error: BOT_TOKEN environment variable not set.")
        sys.exit(1)

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("trained", trained))
    app.add_handler(CommandHandler("progress", progress))
    app.add_handler(CommandHandler("leaderboard", leaderboard))

    print("✅ Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
