import os
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys

print("🚀 Bắt đầu quá trình khởi động bot...")

# --- Kiểm tra TELEGRAM_TOKEN ---
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    print("❌ LỖI NGHIÊM TRỌNG: Biến môi trường 'TELEGRAM_TOKEN' không tồn tại!")
    sys.exit(1)
print("✅ Đã tìm thấy 'TELEGRAM_TOKEN'.")

# --- Kiểm tra SHEET_ID ---
SHEET_ID = os.environ.get("SHEET_ID")
if not SHEET_ID:
    print("❌ LỖI NGHIÊM TRỌNG: Biến môi trường 'SHEET_ID' không tồn tại!")
    sys.exit(1)
print(f"✅ Đã tìm thấy 'SHEET_ID': {SHEET_ID}")

# --- Kiểm tra và Parse GOOGLE_CREDENTIALS ---
creds_json_str = os.environ.get("GOOGLE_CREDENTIALS")
if not creds_json_str:
    print("❌ LỖI NGHIÊM TRỌNG: Biến môi trường 'GOOGLE_CREDENTIALS' không tồn tại!")
    sys.exit(1)
print("✅ Đã tìm thấy 'GOOGLE_CREDENTIALS'. Đang xử lý nội dung JSON...")

try:
    # Thử parse JSON
    creds_dict = json.loads(creds_json_str)
    print("✅ Parse JSON thành công.")
    
    # Thử xác thực với Google
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    print("✅ Xác thực với Google thành công.")
    
    # Thử mở sheet và worksheet cụ thể
    sheet = client.open_by_key(SHEET_ID).worksheet("GiaoDich")
    print("🎉 Kết nối thành công! Bot đã có thể đọc được sheet 'GiaoDich'.")

except Exception as e:
    # In ra lỗi chi tiết
    print(f"❌❌❌ LỖI KẾT NỐI GOOGLE SHEETS: {e}")
    print("Vui lòng kiểm tra lại 'SHEET_ID' và nội dung của 'GOOGLE_CREDENTIALS' (file JSON).")
    sys.exit(1)

# --- Khởi tạo và chạy Bot Telegram ---
print("🤖 Đang khởi tạo bot Telegram...")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Xin chào! Bot MAO đã sẵn sàng và kết nối thành công với Google Sheet của bạn!")

print("✅ Bot Telegram đã sẵn sàng. Bắt đầu lắng nghe lệnh...")
try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Lỗi khi chạy bot: {e}")
    sys.exit(1)
