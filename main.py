from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8533207356:AAHVDfrg_T4WSpeQ0hxeeODswFr_OA6MTK0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(" Paid Course Price", callback_data="Paid Course")],
        [InlineKeyboardButton("💎 Free Fire Diamond Price", callback_data="ff")],
        [InlineKeyboardButton("🎮 BGMI UC Price", callback_data="bgmi")],
        [InlineKeyboardButton("🎁 Google Play Redeem Code", callback_data="redeem")],
        [InlineKeyboardButton("💳 Cards", callback_data="cards")],
        [InlineKeyboardButton("👨‍💼 Customer Support", callback_data="support")]
    ]

    await update.message.reply_text(
        "👋 Welcome to CYBER Cadar\n\nChoose an option below:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "Paid Course":
        text = """Paid Course Price


PAID COURSE BASIC ➜ ₹2000
PAID COURSE BASIC TO PRO ➜ ₹4000

📩 Order: @RT451012"""

    elif query.data == "ff":
        text = """💎 Free Fire Diamond Price

₹700 ➜ 1060 Diamonds
₹1000 ➜ 2180 Diamonds
₹2000 ➜ 5600 Diamonds
₹3500 ➜11200 Diamonds

📩 Order: @CYBERxTRUSTED"""

    elif query.data == "bgmi":
        text = """🎮 BGMI UC Price

₹600 ➜ 660 UC
₹ 1000➜ 1800 UC
₹2000 ➜ 3850 UC
₹3500 ➜ 8100 UC

📩 Order: @CYBERxTRUSTED"""

    elif query.data == "redeem":
        text = """🎁 Google Play Redeem Code

₹1000 ➜ ₹4000 Code
₹2000 ➜ ₹8000 Code
₹2500 ➜ ₹15000 Code
₹3000 ➜ ₹20000 Code
₹5000 ➜ ₹30000 Code

📩 Order: @CYBERxTRUSTED"""

    elif query.data == "cards":
        text = """💳 Cards

 💳 Basic Card

₹1000➜ 10K
₹1500 ➜ 15K
₹2000 ➜ 25K
₹3000➜ 35K
₹5000 ➜ 55K
₹8000 ➜ 1L

👑 Premium Card

₹5000 ➜ 100K
₹10000 ➜ 500K

📩 Order: @CYBERxTRUSTED"""

    elif query.data == "support":
        text = """👨‍💼 Customer Support

📞 Telegram: @CYBERxTRUSTED

💳 UPI ID: 

yunushali@fam



⏰ Reply Time:
5–15 Minutes"""

    keyboard = [[InlineKeyboardButton("🏠 Back", callback_data="home")]]

    if query.data == "home":
        keyboard = [
            [InlineKeyboardButton("🪙 Paid Course", callback_data="Paid Course")],
            [InlineKeyboardButton("💎 Free Fire Diamond Price", callback_data="ff")],
            [InlineKeyboardButton("🎮 BGMI UC Price", callback_data="bgmi")],
            [InlineKeyboardButton("🎁 Google Play Redeem Code", callback_data="redeem")],
            [InlineKeyboardButton("💳 Cards", callback_data="cards")],
            [InlineKeyboardButton("👨‍💼 Customer Support", callback_data="support")]
        ]

        await query.edit_message_text(
            "👋 Welcome to CYBER Cadar\n\nChoose an option below:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("CYBER Cadar Bot Running...")
app.run_polling()