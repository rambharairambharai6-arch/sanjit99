import logging
import random
import string
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ⚠️ Railway par Environment Variable se aayega
BOT_TOKEN = os.getenv("BOT_TOKEN", "8276309713:AAFMvngkplRWx2hXYNi-E6ho9doWQC1ba1o")

# ⚠️ AAPKA CUSTOM DOMAIN
CUSTOM_DOMAIN = "joy.com"

# ⚠️ PREMIUM KE LIYE TELEGRAM USERNAME
PREMIUM_CONTACT = "@JOYxWEB"

DB_FILE = "user_data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def generate_random_username(length=10):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def create_temp_email():
    try:
        username = generate_random_username()
        email_address = f"{username}@{CUSTOM_DOMAIN}"
        return email_address, None
    except Exception as e:
        return None, f"Exception: {str(e)}"

# ---------------- MENU FUNCTION (Buttons Wala) ----------------

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit=False):
    keyboard = [
        [InlineKeyboardButton("📧 New Email", callback_data='new_email')],
        [InlineKeyboardButton("📋 All My Emails", callback_data='all_emails')],
        [InlineKeyboardButton("🚫 Blocked Senders", callback_data='blocked_senders')],
        [InlineKeyboardButton("⭐ Premium Subscription", callback_data='premium')],
        [InlineKeyboardButton("🌐 Change Language", callback_data='change_lang')],
        [InlineKeyboardButton("📱 Update Phone Number", callback_data='update_phone')],
        [InlineKeyboardButton("🗑️ Delete Email", callback_data='delete_email')]
    ]
    
    menu_text = (
        "👋 **Welcome to JOY WRB EMAIL BOT!**\n\n"
        "Main aapki temporary email banane mein madad karunga.\n"
        "📧 Ab saari emails `@joy.com` par banengi.\n\n"
        "Neeche diye gaye buttons use karein:"
    )
    
    if edit:
        await update.callback_query.edit_message_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

# ---------------- COMMAND HANDLERS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    if user_id not in db:
        db[user_id] = {"email": None, "lang": "en", "phone": None, "blocked": []}
        save_db(db)

    await show_main_menu(update, context)

async def new_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    await update.message.reply_text("⏳ Naya email ban raha hai...")
    email, error = create_temp_email()
    
    if email:
        db = load_db()
        db[user_id] = db.get(user_id, {})
        db[user_id]['email'] = email
        if 'blocked' not in db[user_id]: 
            db[user_id]['blocked'] = []
        save_db(db)
        
        await update.message.reply_text(
            f"✅ **Naya Email Ban Gaya!**\n\n"
            f"📧 Email: `{email}`\n\n"
            f"⚠️ Ab is email par OTP aayega. Jab OTP aaye, toh Telegram par hi automatic aa jayega (Cloudflare Worker ke through).",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ Error: {error}")

async def delete_email_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    if user_id in db and db[user_id].get('email'):
        db[user_id]['email'] = None
        save_db(db)
        await update.message.reply_text("✅ Aapka email delete kar diya gaya hai.")
    else:
        await update.message.reply_text("❌ Koi email delete karne ke liye nahi hai.")

async def change_lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    current = db.get(user_id, {}).get('lang', 'en')
    new_lang = 'hi' if current == 'en' else 'en'
    db[user_id]['lang'] = new_lang
    save_db(db)
    
    await update.message.reply_text(f"✅ Language changed to: **{'Hindi' if new_lang == 'hi' else 'English'}**", parse_mode='Markdown')

async def all_emails_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    if user_id in db and db[user_id].get('email'):
        await update.message.reply_text(f"📋 **Aapka Email:**\n`{db[user_id]['email']}`", parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Aapne abhi tak koi email nahi banaya. `/new` command use karein.", parse_mode='Markdown')

async def update_phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📱 Kripya apna phone number type karein (bina +91 ke):")
    context.user_data['phone_mode'] = True

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('phone_mode'):
        return
    
    phone = update.message.text
    context.user_data['phone_mode'] = False
    user_id = str(update.effective_user.id)
    db = load_db()
    db[user_id]['phone'] = phone
    save_db(db)
    
    await update.message.reply_text(f"✅ Phone number saved: `{phone}`", parse_mode='Markdown')

async def blocked_senders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    db = load_db()
    
    blocked = db.get(user_id, {}).get('blocked', [])
    if not blocked:
        await update.message.reply_text("🚫 Aapne abhi tak kisi ko block nahi kiya.")
    else:
        await update.message.reply_text(f"🚫 **Blocked Senders:**\n" + "\n".join([f"• {b}" for b in blocked]))

async def premium_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⭐ **Premium Subscription**\n\n"
        f"Premium lene ke liye is Telegram username par contact karein:\n\n"
        f"👉 {PREMIUM_CONTACT}\n\n"
        f"Filhaal free version bhi use kar sakte hain.",
        parse_mode='Markdown'
    )

# ---------------- BUTTON CALLBACK HANDLER ----------------

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(update.effective_user.id)
    
    if query.data == 'new_email':
        await query.edit_message_text("⏳ Naya email ban raha hai...")
        email, error = create_temp_email()
        
        if email:
            db = load_db()
            db[user_id] = db.get(user_id, {})
            db[user_id]['email'] = email
            if 'blocked' not in db[user_id]: 
                db[user_id]['blocked'] = []
            save_db(db)
            
            await query.edit_message_text(
                f"✅ **Naya Email Ban Gaya!**\n\n"
                f"📧 Email: `{email}`\n\n"
                f"⚠️ Ab is email par OTP aayega. Telegram par hi automatic aa jayega.",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(f"❌ Error: {error}")
            
    elif query.data == 'premium':
        await query.edit_message_text(
            f"⭐ **Premium Subscription**\n\n"
            f"Premium lene ke liye is Telegram username par contact karein:\n\n"
            f"👉 {PREMIUM_CONTACT}\n\n"
            f"Filhaal free version bhi use kar sakte hain.",
            parse_mode='Markdown'
        )
    
    elif query.data == 'all_emails':
        db = load_db()
        if user_id in db and db[user_id].get('email'):
            await query.edit_message_text(f"📋 **Aapka Email:**\n`{db[user_id]['email']}`", parse_mode='Markdown')
        else:
            await query.edit_message_text("❌ Aapne abhi tak koi email nahi banaya.")
            
    elif query.data == 'delete_email':
        db = load_db()
        if user_id in db and db[user_id].get('email'):
            db[user_id]['email'] = None
            save_db(db)
            await query.edit_message_text("✅ Aapka email delete kar diya gaya hai.")
        else:
            await query.edit_message_text("❌ Koi email delete karne ke liye nahi hai.")
            
    elif query.data == 'blocked_senders':
        db = load_db()
        blocked = db.get(user_id, {}).get('blocked', [])
        if not blocked:
            await query.edit_message_text("🚫 Aapne abhi tak kisi ko block nahi kiya.")
        else:
            await query.edit_message_text(f"🚫 **Blocked Senders:**\n" + "\n".join([f"• {b}" for b in blocked]))
            
    elif query.data == 'change_lang':
        db = load_db()
        current = db.get(user_id, {}).get('lang', 'en')
        new_lang = 'hi' if current == 'en' else 'en'
        db[user_id]['lang'] = new_lang
        save_db(db)
        await query.edit_message_text(f"✅ Language changed to: **{'Hindi' if new_lang == 'hi' else 'English'}**", parse_mode='Markdown')
        
    elif query.data == 'update_phone':
        await query.edit_message_text("📱 Kripya apna phone number type karein (bina +91 ke):")
        context.user_data['phone_mode'] = True

# ---------------- MAIN ----------------

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_email_command))
    app.add_handler(CommandHandler("delete", delete_email_command))
    app.add_handler(CommandHandler("lang", change_lang_command))
    app.add_handler(CommandHandler("list", all_emails_command))
    app.add_handler(CommandHandler("update", update_phone_command))
    app.add_handler(CommandHandler("blocked_senders", blocked_senders_command))
    app.add_handler(CommandHandler("premium", premium_command))
    
    # Button Callback Handler
    app.add_handler(CallbackQueryHandler(button_click))
    
    # Text Handler for phone number
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    
    print("🚀 JOY WRB EMAIL BOT chal raha hai... @joy.com emails generate honge!")
    app.run_polling()