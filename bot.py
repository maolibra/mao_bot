import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
from datetime import datetime

# ---------- CẤU HÌNH ----------
TOKEN = "8624405543:AAGSIA7Dted5g1H0Mikdf_D8xHxsyCaXohs"  # 👈 THAY bằng token của bạn
SHEET_ID = "1nIHXLsR5e49wyCNKA70yKqhpUUGAwyk6MoPG7MzAyx8"    # 👈 THAY bằng Sheet ID
# ------------------------------

# Kết nối Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet("GiaoDich")

# Khởi tạo bot
bot = telebot.TeleBot(TOKEN)

def ghi_giao_dich(loai, phan_loai, mo_ta, so_tien):
    """Ghi 1 dòng vào sheet GiaoDich"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, loai, phan_loai, mo_ta, so_tien, ""])
    return True

def xu_ly_thu(message, args):
    """/thu save [mô tả], [số tiền]"""
    try:
        # Tách mô tả và số tiền
        parts = args.split(',')
        mo_ta = parts[0].strip()
        so_tien_nhap = int(parts[1].strip())
        so_tien = so_tien_nhap * 1000
        
        ghi_giao_dich("Thu", "SAVE", mo_ta, so_tien)
        
        quote = "Save trước, tiêu sau 💰"
        bot.reply_to(message, f"{quote}\n\n✅ Bạn vừa nhận được {so_tien_nhap}k ({so_tien:,}đ) tiền {mo_ta}.\nĐã lưu vào kế hoạch của MAO.")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /thu save lương tháng 3, 10000")

def xu_ly_chi(message, args):
    """/chi [save/give/reward] [mô tả], [số tiền]"""
    try:
        # Tách loại và phần còn lại
        parts = args.split(maxsplit=1)
        if len(parts) < 2:
            raise ValueError()
        phan_loai = parts[0].strip().upper()
        if phan_loai not in ["SAVE", "GIVE", "REWARD"]:
            raise ValueError()
        
        # Tách mô tả và số tiền
        desc_parts = parts[1].split(',')
        mo_ta = desc_parts[0].strip()
        so_tien_nhap = int(desc_parts[1].strip())
        so_tien = so_tien_nhap * 1000
        
        ghi_giao_dich("Chi", phan_loai, mo_ta, so_tien)
        
        quote = "Một món đồ không đáng đổi lấy áp lực, Tiêu dễ lắm, giàu mới khó 😤"
        bot.reply_to(message, f"{quote}\n\n✅ Bạn vừa chi {so_tien_nhap}k cho \"{mo_ta}\" từ quỹ {phan_loai}.\nĐã cập nhật vào sổ kế hoạch của MAO.")
    except:
        bot.reply_to(message, "❌ Sai cú pháp. VD: /chi reward mua cà phê, 45")

@bot.message_handler(commands=['thu', 'nhận'])
def thu(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Thiếu thông tin. VD: /thu save lương, 10000")
        return
    xu_ly_thu(message, args[1])

@bot.message_handler(commands=['chi'])
def chi(message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "❌ Thiếu thông tin. VD: /chi reward mua nước, 45")
        return
    xu_ly_chi(message, args[1])

@bot.message_handler(commands=['start', 'help'])
def help_cmd(message):
    bot.reply_to(message, """📌 *Hướng dẫn sử dụng MAO Bot*

/thu save [mô tả], [số nghìn]  
   VD: `/thu save lương tháng 3, 10000`

/chi [save/give/reward] [mô tả], [số nghìn]  
   VD: `/chi reward cà phê, 45`

/tiền [ngày/tuần/tháng] – sắp có

💡 Số tiền nhập là số nghìn (VD: 45 = 45,000đ)""", parse_mode="Markdown")

print("Bot MAO đang chạy...")
bot.infinity_polling()
