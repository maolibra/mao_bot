import os
import json
import logging
from flask import Flask, request
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# Lấy biến môi trường
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
CREDS_JSON = os.environ.get("GOOGLE_CREDENTIALS")

if not TOKEN or not SHEET_ID or not CREDS_JSON:
    logging.error("❌ Thiếu biến môi trường!")
    exit(1)

# Kết nối Google Sheets
try:
    creds_dict = json.loads(CREDS_JSON)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet("GiaoDich")
    logging.info("✅ Kết nối Google Sheets thành công!")
except Exception as e:
    logging.error(f"❌ Lỗi Google Sheets: {e}")
    exit(1)

bot = telebot.TeleBot(TOKEN)

def ghi_giao_dich(loai, phan_loai, mo_ta, so_tien):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, loai, phan_loai, mo_ta, so_tien, ""])

@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    bot.reply_to(message, "📌 /thu save [mô tả], [số nghìn]\n/chi [save/give/reward] [mô tả], [số nghìn]")

@bot.message_handler(commands=['thu', 'nhận'])
def thu(message):
    try:
        parts = message.text.split(maxsplit=1)[1].split(',')
        mo_ta = parts[0].strip()
        so_tien = int(parts[1].strip()) * 1000
        ghi_giao_dich("Thu", "SAVE", mo_ta, so_tien)
        bot.reply_to(message, f"✅ Đã nhận {mo_ta}: {so_tien:,}đ")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /thu save lương, 10000")

@bot.message_handler(commands=['chi'])
def chi(message):
    try:
        text = message.text.split(maxsplit=1)[1]
        phan_loai = text.split()[0].upper()
        rest = text.split(maxsplit=1)[1].split(',')
        mo_ta = rest[0].strip()
        so_tien = int(rest[1].strip()) * 1000
        ghi_giao_dich("Chi", phan_loai, mo_ta, so_tien)
        bot.reply_to(message, f"✅ Đã chi {mo_ta}: {so_tien:,}đ từ quỹ {phan_loai}")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /chi reward cà phê, 45")

@app.route('/')
def index():
    return "Bot is running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    try:
        update = telebot.types.Update.de_json(request.get_data().decode('UTF-8'))
        bot.process_new_updates([update])
        return '', 200
    except:
        return '', 200

if __name__ == "__main__":
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    logging.info(f"✅ Webhook set: {webhook_url}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
