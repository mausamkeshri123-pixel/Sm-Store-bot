import telebot
from telebot.types import *
import sqlite3

# ================= CONFIG =================
TOKEN = "8606274819:AAGvQjCsYPyLbdPpeQasw_UPbDVfVGiP0-0"
ADMIN_ID = 8743944782
LOG_CHANNEL = "@SmStoreLogs"

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# ================= DATABASE =================
conn = sqlite3.connect("store.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER DEFAULT 0)")
cursor.execute("CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, data TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS prices (category TEXT PRIMARY KEY, price INTEGER)")
conn.commit()

# ================= CHANNEL CHECK =================
def is_joined(user_id):
    try:
        channels = [
            "@SmStoreLiveDrops",
            "@Smstorelogs",
            "@SmStoreUpdates"
        ]

        for ch in channels:
            status = bot.get_chat_member(ch, user_id).status
            if status in ["left", "kicked"]:
                return False
        return True
    except:
        return False

# ================= FORCE JOIN =================
def force_join(msg):
    btn = InlineKeyboardMarkup()

    btn.add(InlineKeyboardButton("📉 𝗦𝗠 𝗦𝘁𝗼𝗿𝗲 𝗟𝗶𝘃𝗲 𝗗𝗿𝗼𝗽𝘀", url="https://t.me/SmStoreLiveDrops"))
    btn.add(InlineKeyboardButton("💙 𝗦𝗠 𝗦𝘁𝗼𝗿𝗲 𝗟𝗼𝗴𝘀", url="https://t.me/Smstorelogs"))
    btn.add(InlineKeyboardButton("📢 𝗦𝗺 𝗦𝘁𝗼𝗿𝗲 𝗨𝗽𝗱𝗮𝘁𝗲𝘀!", url="https://t.me/SmStoreUpdates"))

    btn.add(InlineKeyboardButton("✅ Check Again", callback_data="check_join"))

    bot.send_message(
        msg.chat.id,
        """⚠️ Access Restricted!

You must join our mandatory channels before using the bot:

📉 𝗦𝗠 𝗦𝘁𝗼𝗿𝗲 𝗟𝗶𝘃𝗲 𝗗𝗿𝗼𝗽𝘀  
💙 𝗦𝗠 𝗦𝘁𝗼𝗿𝗲 𝗟𝗼𝗴𝘀  
📢 𝗦𝗺 𝗦𝘁𝗼𝗿𝗲 𝗨𝗽𝗱𝗮𝘁𝗲𝘀!

Click 'Check Again' after joining!""",
        reply_markup=btn
    )

# ================= MENU =================
def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("IG Accounts ⭐", "Email ✉️")
    m.row("TG Accounts 🌎", "Smm services 🚀")
    m.row("Deposit 🏧", "Balance 💸")
    return m

# ================= START =================
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id

    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
    conn.commit()

    if not is_joined(uid):
        force_join(msg)
        return

    bot.send_message(uid, "🌎 Sm Store\n👇 Choose below 👇", reply_markup=menu())

# ================= CHECK AGAIN =================
@bot.callback_query_handler(func=lambda c: c.data == "check_join")
def check_join(call):
    if is_joined(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Welcome Back!", reply_markup=menu())
    else:
        bot.answer_callback_query(call.id, "❌ Join all channels first!", show_alert=True)

# ================= PRODUCT =================
def product(msg, cat, title):
    cursor.execute("SELECT price FROM prices WHERE category=?", (cat,))
    p = cursor.fetchone()

    price = p[0] if p else 0

    cursor.execute("SELECT COUNT(*) FROM accounts WHERE category=?", (cat,))
    stock = cursor.fetchone()[0]

    text = f"""{title}

💰 Price: ₹{price}
📦 Stock: {stock}
"""

    btn = InlineKeyboardMarkup()
    btn.add(InlineKeyboardButton("Confirm Purchase ✅", callback_data=f"buy_{cat}"))
    btn.add(InlineKeyboardButton("🔙 Back", callback_data="back"))

    bot.send_message(msg.chat.id, text, reply_markup=btn)

# ================= BACK =================
@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    bot.send_message(call.message.chat.id, "👇 Menu", reply_markup=menu())

# ================= BUTTONS =================
@bot.message_handler(func=lambda m: m.text == "IG Accounts ⭐")
def ig(msg):
    product(msg, "instagram", "Instagram Accounts ⭐")

@bot.message_handler(func=lambda m: m.text == "Email ✉️")
def email(msg):
    product(msg, "email", "Email Accounts ✉️")

@bot.message_handler(func=lambda m: m.text == "TG Accounts 🌎")
def tg(msg):
    bot.send_message(msg.chat.id, "TG Accounts 🌎 Opened")

@bot.message_handler(func=lambda m: m.text == "Smm services 🚀")
def smm(msg):
    bot.send_message(msg.chat.id, "SMM Services 🚀 Opened")

# ================= BALANCE =================
@bot.message_handler(func=lambda m: m.text == "Balance 💸")
def balance(msg):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (msg.from_user.id,))
    b = cursor.fetchone()[0]
    bot.send_message(msg.chat.id, f"💸 Balance: ₹{b}")

# ================= BUY SYSTEM =================
@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def buy(call):
    cat = call.data.split("_")[1]
    uid = call.from_user.id

    cursor.execute("SELECT price FROM prices WHERE category=?", (cat,))
    p = cursor.fetchone()

    if not p:
        bot.answer_callback_query(call.id, "❌ Price not set")
        return

    price = p[0]

    cursor.execute("SELECT balance FROM users WHERE user_id=?", (uid,))
    bal = cursor.fetchone()[0]

    if bal < price:
        bot.answer_callback_query(call.id, "❌ Low Balance")
        return

    cursor.execute("SELECT * FROM accounts WHERE category=? LIMIT 1", (cat,))
    acc = cursor.fetchone()

    if not acc:
        bot.answer_callback_query(call.id, "❌ Out of Stock")
        return

    new_bal = bal - price
    cursor.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, uid))

    cursor.execute("DELETE FROM accounts WHERE id=?", (acc[0],))
    conn.commit()

    # USER
    bot.send_message(uid, f"""✅ Purchase Successful

📦 {cat.upper()}
👤 {acc[2]}
💰 Deducted: ₹{price}
💸 Left: ₹{new_bal}
""")

    # LOG
    bot.send_message(
        LOG_CHANNEL,
        f"""🚀 NEW ACCOUNT SOLD!

👤 User: {str(uid)[:2]}***{str(uid)[-3:]}
📦 Item: {cat.upper()}
💰 Price: ₹{price}
💸 Balance: ₹{new_bal}
📱 Account: {acc[2][:3]}****{acc[2][-2:]}

🤖 @SmStoreRobot"""
    )

# ================= RUN =================
bot.infinity_polling()