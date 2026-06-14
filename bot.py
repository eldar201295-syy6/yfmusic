import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import os
import telebot
import imageio_ffmpeg as ffmpeg  # Автоматический поиск встроенного FFmpeg
from yt_dlp import YoutubeDL
# 1 и 2 строчка (Импорты)
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Сразу под ними — наш большой кусок-обманщик для Render
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# А вот уже дальше идет ТВОЙ старый код (import telebot, токен и т.д.)
import telebot
# ...весь твой остальной код бота...
# Сюда вставь свой токен внутри кавычек

BOT_TOKEN = '8208930164:AAEqpHGxeVa6VYtKmCE6eJse3QEHQe286jQ' 
bot = telebot.TeleBot(BOT_TOKEN)

# Получаем путь к установленному FFmpeg
FFMPEG_EXE = ffmpeg.get_ffmpeg_exe()

            ydl_opts = {'ffmpeg_location': ffmpeg.get_ffmpeg_exe(),
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl': '%(title)s.%(ext)s',
    'ffmpeg_location': FFMPEG_EXE,  # Указываем прямой путь к встроенному FFmpeg
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True,
}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Напиши название песни или исполнителя.")

@bot.message_handler(func=lambda message: True)
def search_and_send_audio(message):
    query = message.text
    status_msg = bot.reply_to(message, "Ищу и скачиваю... ⏳")
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if not info['entries']:
                bot.edit_message_text("Не найдено.", message.chat.id, status_msg.message_id)
                return
            
            video_info = info['entries'][0]
            title = video_info['title']
            file_name = f"{title}.mp3"
            
        with open(file_name, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=title)
            
        os.remove(file_name)
        bot.delete_message(message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Ошибка в консоли: {e}")
        bot.edit_message_text("Ошибка при скачивании.", message.chat.id, status_msg.message_id)
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)

if __name__ == '__main__':
    print("Бот успешно запущен со встроенным FFmpeg!")
    bot.infinity_polling()