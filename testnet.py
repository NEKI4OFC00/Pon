import telebot
from telebot import types
import sqlite3
import random
import string
from datetime import datetime, timedelta
import threading
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from time import sleep

# Замените на ваши учетные данные и email аккаунты
EMAIL_ACCOUNTS = [
    {'email': 'nik.sokolovskiy.2025@mail.ru', 'password': '05092016A0+7D'}
    # Добавьте другие почтовые аккаунты сюда
]
EMAIL_ADDRESSES = [
    'security@telegram.org',
    'sms@telegram.org',
    'stopCA@telegram.org',
    'abuse@telegram.org',
    'dmca@telegram.org'
]

BOT_TOKEN = '7219521716:AAFm3jUeIL4VDBEJHuwE8kBxHkrRoYScnAc'
ADMIN_IDS = [6665308361]
PROMO_ADMIN_IDS = [6665308361, 7168398511]  # Пример ID промо-админов

bot = telebot.TeleBot(BOT_TOKEN)

# Создаем базу данных для рефералов и промокодов
conn = sqlite3.connect('referrals.db', check_same_thread=False)

# Создаем таблицы, если они еще не существуют
with conn:
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER PRIMARY KEY,
            referrer_id INTEGER,
            invited_count INTEGER DEFAULT 0,
            first_time BOOLEAN DEFAULT 1
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocodes (
            code TEXT PRIMARY KEY,
            duration INTEGER,
            used BOOLEAN DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_promotions (
            user_id INTEGER PRIMARY KEY,
            end_time TIMESTAMP
        )
    ''')

def generate_promocode(prefix):
    code = prefix + ''.join(random.choice(string.ascii_uppercase) for _ in range(5))
    code += random.choice(string.digits + '#&!?')
    return code

def save_user_data():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_promotions')
    users = cursor.fetchall()
    with open('user_data.txt', 'w') as f:
        for user in users:
            user_id, end_time = user
            f.write(f'{user_id},{end_time}\n')

def load_user_data():
    file_path = 'user_data.txt'
    if os.path.exists(file_path):
        cursor = conn.cursor()
        with open(file_path, 'r') as f:
            for line in f:
                user_id, end_time = line.strip().split(',')
                cursor.execute('INSERT OR REPLACE INTO user_promotions (user_id, end_time) VALUES (?, ?)', (user_id, end_time))
        conn.commit()
    else:
        print(f"File {file_path} does not exist")

def schedule_updates():
    threading.Timer(1800, schedule_updates).start()
    save_user_data()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    cursor = conn.cursor()
    
    cursor.execute('SELECT first_time FROM referrals WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    if not result:
        referrer_id = message.text.split("?start=")[-1] if '?start=' in message.text else None
        cursor.execute('INSERT INTO referrals (user_id, referrer_id, invited_count, first_time) VALUES (?, 0, 1)', (user_id, referrer_id))
        conn.commit()

        if referrer_id is not None:
            cursor.execute('UPDATE referrals SET invited_count = invited_count + 1 WHERE user_id = ?', (referrer_id,))
            conn.commit()
    else:
        referrer_id = None

    cursor.execute('UPDATE referrals SET first_time = 0 WHERE user_id = ?', (user_id,))
    conn.commit()

    referral_link = f"https://t.me/{bot.get_me().username}?start={user_id}"

    cursor.execute('SELECT invited_count FROM referrals WHERE user_id = ?', (user_id,))
    invited_count = cursor.fetchone()[0]

    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("Купить подписку", callback_data="buy_subscription"),
        types.InlineKeyboardButton("Рефералка", callback_data="referral")
    )
    
    if user_id in ADMIN_IDS:
        markup.row(types.InlineKeyboardButton("Создать промокод", callback_data="create_promocode"))
    
    cursor.execute('SELECT end_time FROM user_promotions WHERE user_id = ?', (user_id,))
    promotion = cursor.fetchone()
    if promotion and datetime.strptime(promotion[0], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
        markup.row(types.InlineKeyboardButton("Снос", callback_data="snos"))

    markup.row(types.InlineKeyboardButton("Оставшееся время", callback_data="remaining_time"))

    bot.send_message(message.chat.id, 
        "Добро пожаловать в MIDEROV SNOS!\n\n"
        "С помощью нашего бота вы сможете отправлять большое количество жалоб на пользователей и их каналы\n"
        "Приобретите подписку по кнопке ниже!",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    user_id = call.from_user.id
    cursor = conn.cursor()
    
    if call.data == "buy_subscription":
        bot.answer_callback_query(call.id, text="Выберите продолжительность подписки:")

        price_text = ("Прайс данного бота💸\n"
                     "1 день - 50₽\n"
                     "1 неделя - 150₽\n"
                     "1 месяц - 400₽\n"
                     "1 год - 1000₽\n"
                     "навсегда - 3500₽\n\n"
                     "Писать по поводу покупки📥 - @liderdoxa\n"
                     "Так же, если вы хотите приобрести сразу много ключей условно под раздачу, то возможен опт🔥")

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=price_text,
            reply_markup=markup
        )

    elif call.data == "referral":
        referral_link = f"https://t.me/{bot.get_me().username}?start={call.from_user.id}"

        cursor.execute('SELECT invited_count FROM referrals WHERE user_id = ?', (call.from_user.id,))
        
        result = cursor.fetchone()
        invited_count = result[0] if result else 0

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Приглашая по данной ссылке пользователей в бота вы будете получать 20% времени с купленной ими подписки\n\n"
            f"Ваша ссылка: {referral_link}\n\n"
            f"Количество приглашенных: {invited_count}",
            reply_markup=markup
        )

    elif call.data == "create_promocode":
        if user_id in PROMO_ADMIN_IDS:
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton("2 часа", callback_data="create_2h"),
                types.InlineKeyboardButton("1 день", callback_data="create_1d")
            )
            markup.row(
                types.InlineKeyboardButton("1 неделя", callback_data="create_1w"),
                types.InlineKeyboardButton("1 месяц", callback_data="create_1m"),
                types.InlineKeyboardButton("1 год", callback_data="create_1y"),
                types.InlineKeyboardButton("навсегда", callback_data="create_forever")
            )
            markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="Выберите продолжительность для создания промокода:",
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "У вас нет прав на создание промокодов.")

    elif call.data.startswith("create_"):
        if user_id in PROMO_ADMIN_IDS:
            duration_map = {
                "2h": timedelta(hours=2),
                "1d": timedelta(days=1),
                "1w": timedelta(weeks=1),
                "1m": timedelta(days=30),
                "1y": timedelta(days=365),
                "forever": timedelta(days=36500)  # ~100 years
            }

            duration_key = call.data.split("_")[1]
            duration = duration_map.get(duration_key)

            if duration:
                promocode = generate_promocode("PROMO_")
                cursor.execute('INSERT INTO promocodes (code, duration) VALUES (?, ?)', (promocode, duration.total_seconds()))
                conn.commit()

                markup = types.InlineKeyboardMarkup()
                markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

                bot.send_message(
                    call.message.chat.id,
                    text=f"Промокод успешно создан: {promocode}\nС его помощью вы получите подписку на {duration}",
                    reply_markup=markup
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    "Ошибка при создании промокода. Попробуйте еще раз."
                )
        else:
            bot.answer_callback_query(call.id, "У вас нет прав на создание промокодов.")

    elif call.data == "remaining_time":
        cursor.execute('SELECT end_time FROM user_promotions WHERE user_id = ?', (user_id,))
        promotion = cursor.fetchone()
        
        if promotion and datetime.strptime(promotion[0], '%Y-%m-%d %H:%M:%S.%f') > datetime.now():
            remaining_time = datetime.strptime(promotion[0], '%Y-%m-%d %H:%M:%S.%f') - datetime.now()
            remaining_days = remaining_time.days
            remaining_hours = remaining_time.seconds // 3600
            remaining_minutes = (remaining_time.seconds % 3600) // 60

            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"Оставшееся время подписки: {remaining_days} дн. {remaining_hours} ч. {remaining_minutes} мин.",
                reply_markup=markup
            )
        else:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("Назад", callback_data="main_menu"))

            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="У вас нет активной подписки.",
                reply_markup=markup
            )

    elif call.data == "snos":
        bot.send_message(call.message.chat.id, "Отправьте текст жалобы для начала сноса:")

        bot.register_next_step_handler(call.message, handle_complaint)

    elif call.data == "main_menu":
        send_welcome(call.message)

def handle_complaint(message):
    user_id = message.from_user.id
    complaint_text = message.text

    # Удаляем сообщение с просьбой отправить текст для начала сноса и сам текст жалобы
    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.delete_message(message.chat.id, message.message_id)

    # Уведомляем администратора
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, f"Новый запрос от {message.from_user.username or message.from_user.id}\nТекст: {complaint_text}")

    bot.send_message(message.chat.id, "Ожидайте начала рассылки...")

    delay = random.randint(30, 40)
    sleep(delay)

    # Отправка жалобы на почту
    process_complaint(user_id, complaint_text)

def process_complaint(user_id, complaint_text):
    # Функция для отправки жалобы на почту и уведомления пользователю

    send_email(complaint_text)

    bot.send_message(
        user_id,
        "Ваша жалоба была успешно отправлена с 439 почт✅\nОжидайте сноса☕"
    )

def send_email(complaint_text):
    # Функция для отправки письма на почту

    for email_account in EMAIL_ACCOUNTS:
        email = email_account['email']
        password = email_account['password']

        subject = "Жалоба на нарушение"
        body = f"Новый запрос на жалобу:\n\n{complaint_text}"

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = ", ".join(EMAIL_ADDRESSES)
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
            server.ehlo()
            server.login(email, password)
            server.sendmail(email, EMAIL_ADDRESSES, msg.as_string())
            server.close()
        except Exception as e:
            print(f"Failed to send email: {str(e)}")

if __name__ == "__main__":
    load_user_data()
    schedule_updates()
    bot.polling(none_stop=True)