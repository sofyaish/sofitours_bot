# -*- coding: utf-8 -*-
import telebot
from telebot import types
import os
import requests
import psycopg2
from urllib.parse import urlparse

# Получаем токены из переменных окружения Railway
TOKEN = os.environ.get('BOT_TOKEN')
TP_TOKEN = os.environ.get('TP_TOKEN')
DATABASE_URL = os.environ.get('DATABASE_URL')

bot = telebot.TeleBot(TOKEN)

# --- ФУНКЦИЯ ДЛЯ СОХРАНЕНИЯ ПОЛЬЗОВАТЕЛЯ В SUPABASE ---
def save_user_to_db(chat_id, username, first_name):
    if not DATABASE_URL:
        return
    try:
        url = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        cursor = conn.cursor()
        
        # Сохраняем пользователя или пропускаем, если chat_id уже существует
        cursor.execute(
            """
            INSERT INTO users (chat_id, username, first_name) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (chat_id) DO NOTHING;
            """,
            (chat_id, username, first_name)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка сохранения в базу данных: {e}")
# --------------------------------------------------------

# Функция для перевода названия города в IATA-код
def get_iata_code(city_name):
    try:
        url = f"http://autocomplete.travelpayouts.com/places2?term={city_name}&locale=ru&types[]=city"
        response = requests.get(url)
        data = response.json()
        if data:
            return data[0]['code']
    except Exception:
        return None
    return None

# Функция для перевода IATA-кода обратно в название города
def get_city_name(iata_code):
    try:
        url = f"http://autocomplete.travelpayouts.com/places2?term={iata_code}&locale=ru"
        response = requests.get(url)
        data = response.json()
        if data:
            for place in data:
                if place.get('code') == iata_code:
                    return place.get('name')
            return data[0].get('name', iata_code)
    except Exception:
        return iata_code
    return iata_code

@bot.message_handler(commands=['start'])
def start_message(message):
    # Сохраняем пользователя в облачную базу
    save_user_to_db(message.chat.id, message.from_user.username, message.from_user.first_name)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("🔥 Горящие туры")
    btn2 = types.KeyboardButton("✈️ Авиабилеты")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id, 
        "Здравствуйте! 👋\n\nДобро пожаловать в официального бота SofiTours.\nЗдесь вы можете найти лучшие предложения для вашего отдыха!\n\nВыберите нужный раздел в меню ниже:", 
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "🔥 Горящие туры":
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        
        btn_thailand = types.InlineKeyboardButton("🇹🇭 Таиланд", url="https://travelata.tpk.ro/cpWK1dYQ")
        btn_turkey = types.InlineKeyboardButton("🇹🇷 Турция", url="https://travelata.tpk.ro/GhxyG6te")
        btn_vietnam = types.InlineKeyboardButton("🇻🇳 Вьетнам", url="https://travelata.tpk.ro/g6CALGk1")
        btn_tunisia = types.InlineKeyboardButton("🇹🇳 Тунис", url="https://travelata.tpk.ro/VR7pcw6Y")
        btn_egypt = types.InlineKeyboardButton("🇪🇬 Египет", url="https://travelata.tpk.ro/8wm6Mjph")
        btn_india = types.InlineKeyboardButton("🇮🇳 Индия", url="https://travelata.tpk.ro/BjrZ9y0k")
        btn_uae = types.InlineKeyboardButton("🇦🇪 ОАЭ", url="https://travelata.tpk.ro/MnQp9ERC")
        btn_maldives = types.InlineKeyboardButton("🇲🇻 Мальдивы", url="https://travelata.tpk.ro/DJGw3rpf")
        btn_russia = types.InlineKeyboardButton("🇷🇺 Россия", url="https://travelata.tpk.ro/AoSBnh7u")
        
        inline_markup.add(
            btn_thailand, btn_turkey, 
            btn_vietnam, btn_tunisia, 
            btn_egypt, btn_india, 
            btn_uae, btn_maldives, 
            btn_russia
        )
        
        bot.send_message(
            message.chat.id, 
            "Я подготовил для вас подборки лучших предложений! 🌴\n\nВыберите страну, чтобы посмотреть актуальные цены и забронировать тур:", 
            reply_markup=inline_markup
        )
        
    elif message.text == "✈️ Авиабилеты":
        msg = bot.send_message(
            message.chat.id, 
            "Откуда вы летите? 🛫\n\nНапишите название города (например, Москва, Томск или Казань):"
        )
        bot.register_next_step_handler(msg, process_flight_search)
        
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки меню внизу экрана.")

def process_flight_search(message):
    if message.text in ["🔥 Горящие туры", "✈️ Авиабилеты"]:
        handle_text(message)
        return

    city_name = message.text.strip()
    iata_code = get_iata_code(city_name)
    
    if not iata_code:
        msg = bot.send_message(
            message.chat.id, 
            f"К сожалению, я не нашел аэропорт для города «{city_name}». Проверьте опечатку и попробуйте еще раз (например, Москва):"
        )
        bot.register_next_step_handler(msg, process_flight_search)
        return

    bot.send_message(message.chat.id, f"Ищу дешевые билеты из г. {city_name} (код {iata_code})... ⏳")
    
    try:
        url = "https://api.travelpayouts.com/v2/prices/latest"
        headers = {'x-access-token': TP_TOKEN}
        params = {
            'origin': iata_code,
            'currency': 'rub',
            'limit': 3,
            'show_to_affiliates': 'true'
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get('success') and data.get('data'):
            tickets = data['data']
            for ticket in tickets:
                origin_name = get_city_name(ticket['origin'])
                dest_name = get_city_name(ticket['destination'])
                
                date_parts = ticket['depart_date'].split('-')
                day_month = date_parts[2] + date_parts[1]
                
                affiliate_link = f"https://aviasales.ru/search/{ticket['origin']}{day_month}{ticket['destination']}1?marker=59114"
                
                ticket_markup = types.InlineKeyboardMarkup()
                btn_buy = types.InlineKeyboardButton("✈️ Посмотреть билеты", url=affiliate_link)
                ticket_markup.add(btn_buy)
                
                text = (
                    f"✈️ *Направление: {origin_name} ({ticket['origin']}) ➔ {dest_name} ({ticket['destination']})*\n"
                    f"💰 Цена: от {ticket['value']} руб.\n"
                    f"📅 Вылет: {ticket['depart_date']}"
                )
                
                bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=ticket_markup)
        else:
            bot.send_message(message.chat.id, f"К сожалению, сейчас не удалось найти билеты из г. {city_name}. Попробуйте позже.")
            
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при обращении к серверу билетов.")

if __name__ == '__main__':
    print("Бот SofiTours успешно запущен!")
    bot.polling(none_stop=True)
