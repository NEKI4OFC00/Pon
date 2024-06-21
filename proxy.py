import telebot
import time
import requests
from telebot import types

TOKEN = '7073943018:AAGUteLIZxIHqVt9TWTYFhDgh0Zby_V-D8s'  # Замените на ваш токен бота
bot = telebot.TeleBot(TOKEN)

# Словарь с ссылками на файлы
proxy_files = {
    'all': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/all.txt',
    'all_no_port': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/all_no_ports.txt',
    'http': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/http.txt',
    'https': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/https.txt',
    'socks4': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks4.txt',
    'socks5': 'https://raw.githubusercontent.com/Tsprnay/Proxy-lists/master/proxies/socks5.txt',
}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.type == 'private':
        bot.reply_to(message, "Добавьте меня в любой чат для начала работы🛠️, Создатели: @TALISOV_ONE , @arcteryx_team (кодер☕)")
    else:
        bot.reply_to(message, "Здравствуйте, я бот созданный для чата TwT по отправке прокси, и проверки скорости ответа телеграмм. Ссылка на наш проект: https://t.me/twtproject")
        # Предоставление прав администратора 
        admin_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

@bot.message_handler(commands=['ping'])
def send_ping(message):
    start_time = time.time()
    msg = bot.reply_to(message, "Проверка времени ответа⌛...")
    end_time = time.time()
    bot.edit_message_text(f"Ответ бота: {int((end_time - start_time) * 1000)} мс⚡", message.chat.id, msg.message_id)

@bot.message_handler(commands=['proxy'])
def send_proxy_menu(message):
    bot.reply_to(message, "Выберите тип желаемых прокси и напишите в ответ на это сообщение (All/Socks4/Socks5/Http/Https), так же не забывайте что все прокси обновляются каждые 20 минут!🕘")

@bot.message_handler(func=lambda message: message.text in proxy_files)
def handle_proxy_request(message):
    proxy_type = message.text.lower()
    file_url = proxy_files[proxy_type]

    bot.reply_to(message, f"Получение прокси в формате {proxy_type} ⏳")

    try:
        response = requests.get(file_url)
        response.raise_for_status()  # Проверка кода ответа (200 - OK)

        # Сохранение файла
        with open('proxies.txt', 'wb') as f:
            f.write(response.content)

        # Отправка файла в качестве ответа на сообщение
        with open('proxies.txt', 'rb') as f:
            bot.send_document(chat_id=message.chat.id, document=f, caption=f"Вот ваши прокси в формате {proxy_type}")

    except requests.exceptions.RequestException as e:
        bot.reply_to(message, f"Ошибка при получении прокси: {e}")

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_members(message):
    for member in message.new_chat_members:
        bot.reply_to(message, f"Добро пожаловать в чат, {member.first_name}! Прочитай лучше сразу правила❗")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye_member(message):
    bot.reply_to(message, "Прощай")

bot.polling()