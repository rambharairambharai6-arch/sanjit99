from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "8889622689:AAFYiVx8Z5J9G_uVpmUlfGhc9g6kRQs5quk"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "User"

    text = (
        f"✅ THANK YOU FOR CONFIRMING, {name}!\n\n"
        "You Can Now Use The Bot's Features.\n\n"
        "Send /id To Get Your Chat ID"
    )

    await update.message.reply_text(text)

async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    await update.message.reply_text(
        f"🪪 Your Chat ID is:\n{chat_id}\n\n👉 Click Here To Copy"
    )

app = Application.builder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("id", chat_id))

print("Bot Started...")

app.run_polling()