import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
from datetime import datetime
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# ---------- CẤU HÌNH ----------
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SHEET_ID = os.environ.get("SHEET_ID")
# ------------------------------

# Kiểm tra biến môi trường
if not TOKEN or not SHEET_ID:
    print("❌ LỖI: Thiếu TELEGRAM_TOKEN hoặc SHEET_ID trong biến môi trường!")
    exit(1)

# Kết nối Google Sheets từ biến môi trường GOOGLE_CREDENTIALS
creds_json = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json:
    print("❌ LỖI: Thiếu GOOGLE_CREDENTIALS trong biến môi trường!")
    exit(1)

try:
    creds_dict = json.loads(creds_json)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet("GiaoDich")
    print("✅ Kết nối Google Sheets thành công!")
except Exception as e:
    print(f"❌ Lỗi kết nối Google Sheets: {e}")
    exit(1)

# Khởi tạo bot
bot = telebot.TeleBot(TOKEN)

def ghi_giao_dich(loai, phan_loai, mo_ta, so_tien):
    """Ghi 1 dòng vào sheet GiaoDich"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, loai, phan_loai, mo_ta, so_tien, ""])
    return True

@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    bot.reply_to(message, """📌 *Hướng dẫn sử dụng MAO Bot*

/thu save [mô tả], [số nghìn]  
   VD: `/thu save lương tháng 3, 10000`

/chi [save/give/reward] [mô tả], [số nghìn]  
   VD: `/chi reward cà phê, 45`

💡 Số tiền nhập là số nghìn (VD: 45 = 45,000đ)""", parse_mode="Markdown")

@bot.message_handler(commands=['thu', 'nhận'])
def thu(message):
    try:
        text = message.text.split(maxsplit=1)[1]
        parts = text.split(',')
        mo_ta = parts[0].strip()
        so_tien_nhap = int(parts[1].strip())
        so_tien = so_tien_nhap * 1000
        
        ghi_giao_dich("Thu", "SAVE", mo_ta, so_tien)
        
        quote = "Save trước, tiêu sau 💰"
        bot.reply_to(message, f"{quote}\n\n✅ Bạn vừa nhận được {so_tien_nhap}k ({so_tien:,}đ) tiền {mo_ta}.\nĐã lưu vào kế hoạch của MAO.")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /thu save lương, 10000")

@bot.message_handler(commands=['chi'])
def chi(message):
    try:
        text = message.text.split(maxsplit=1)[1]
        parts = text.split(maxsplit=1)
        phan_loai = parts[0].strip().upper()
        if phan_loai not in ["SAVE", "GIVE", "REWARD"]:
            raise ValueError()
        
        desc_parts = parts[1].split(',')
        mo_ta = desc_parts[0].strip()
        so_tien_nhap = int(desc_parts[1].strip())
        so_tien = so_tien_nhap * 1000
        
        ghi_giao_dich("Chi", phan_loai, mo_ta, so_tien)
        
        quote = "Một món đồ không đáng đổi lấy áp lực, Tiêu dễ lắm, giàu mới khó 😤"
        bot.reply_to(message, f"{quote}\n\n✅ Bạn vừa chi {so_tien_nhap}k cho \"{mo_ta}\" từ quỹ {phan_loai}.\nĐã cập nhật vào sổ kế hoạch của MAO.")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /chi reward mua cà phê, 45")

# ----- GIẢ LẬP WEB SERVER ĐỂ GIỮ BOT CHẠY TRÊN RENDER -----
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    
    def log_message(self, format, *args):
        pass  # Im lặng log của web server

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"✅ Health check server đang chạy trên cổng {port}")
    server.serve_forever()

# Chạy web server trong luồng riêng
threading.Thread(target=run_health_server, daemon=True).start()

# Chạy bot
print("🚀 Bot MAO đang chạy...")
try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Lỗi bot: {e}")
