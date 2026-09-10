# -*- coding: utf-8 -*-
import telebot
from telebot import types
import os
import requests # Библиотека для работы с API

# Получаем токены из Railway
TOKEN = os.environ.get('BOT_TOKEN')
TP_TOKEN = os.environ.get('TP_TOKEN') # Ваш токен Travelpayouts

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
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
    if message.text == "✈️ Авиабилеты":
        bot.send_message(message.chat.id, "Ищу дешевые билеты из Москвы... ⏳")
        
        try:
            # Обращаемся к API Авиасейлс (Travelpayouts)
            url = "https://api.travelpayouts.com/v2/prices/latest"
            headers = {'x-access-token': TP_TOKEN}
            
            # Параметры: вылет из Москвы (MOW), цены в рублях, берем 3 самых дешевых билета
            params = {
                'origin': 'MOW',
                'currency': 'rub',
                'limit': 3,
                'show_to_affiliates': 'true'
            }
            
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get('success') and data.get('data'):
                tickets = data['data']
                for ticket in tickets:
                    # Формируем красивую карточку билета
                    text = (
                        f"✈️ *Направление: {ticket['origin']} ➔ {ticket['destination']}*\n"
                        f"💰 Цена: {ticket['value']} руб.\n"
                        f"📅 Вылет: {ticket['depart_date']}\n\n"
                        f"🔗 [Найти на сайте](https://sofitours.ru/)" # Здесь в будущем можно вставить вашу партнерскую ссылку
                    )
                    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)
            else:
                bot.send_message(message.chat.id, "К сожалению, сейчас не удалось найти билеты. Попробуйте позже.")
                
        except Exception as e:
            bot.send_message(message.chat.id, "Произошла ошибка при обращении к серверу билетов.")
            
    elif message.text == "🔥 Горящие туры":
        # Создаем клавиатуру в 2 столбца для красоты
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        
        # Все ваши готовые партнерские ссылки
        btn_thailand = types.InlineKeyboardButton("Таиланд", url="https://travelata.tpk.ro/cpWK1dYQ")
        btn_turkey = types.InlineKeyboardButton("Турция", url="https://travelata.tpk.ro/GhxyG6te")
        btn_vietnam = types.InlineKeyboardButton("Вьетнам", url="https://travelata.tpk.ro/g6CALGk1")
        btn_tunisia = types.InlineKeyboardButton("Тунис", url="https://travelata.tpk.ro/VR7pcw6Y")
        btn_egypt = types.InlineKeyboardButton("Египет", url="https://travelata.tpk.ro/8wm6Mjph")
        btn_india = types.InlineKeyboardButton("Индия", url="https://travelata.tpk.ro/BjrZ9y0k")
        btn_uae = types.InlineKeyboardButton("ОАЭ", url="https://travelata.tpk.ro/MnQp9ERC")
        btn_maldives = types.InlineKeyboardButton("Мальдивы", url="https://travelata.tpk.ro/DJGw3rpf")
        btn_russia = types.InlineKeyboardButton("Россия", url="https://travelata.tpk.ro/AoSBnh7u")
        
        # Добавляем все кнопки в меню
        inline_markup.add(
            btn_thailand, btn_turkey, 
            btn_vietnam, btn_tunisia, 
            btn_egypt, btn_india, 
            btn_uae, btn_maldives, 
            btn_russia
        )
        
        bot.send_message(
            message.chat.id, 
            "Я подготовила для вас подборки лучших предложений! 🌴\n\nВыберите страну, чтобы посмотреть актуальные цены и забронировать тур:", 
            reply_markup=inline_markup
        )

if __name__ == '__main__':
    print("Бот SofiTours успешно запущен!")
    bot.polling(none_stop=True)
