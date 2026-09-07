# -*- coding: utf-8 -*-
import telebot
from telebot import types

import os
TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    # Создаем клавиатуру
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
        # Временная заглушка для туров
        bot.send_message(
            message.chat.id, 
            "Ищу самые свежие горящие туры... ⏳\n\n*(Здесь скоро будет подключено API для вывода реальных туров с сайта)*", 
            parse_mode="Markdown"
        )
        
    elif message.text == "✈️ Авиабилеты":
        # Временная заглушка для билетов
        bot.send_message(
            message.chat.id, 
            "Ищу дешевые билеты за последние 72 часа... ⏳\n\n*(Здесь скоро будет подключено API от Travelpayouts)*", 
            parse_mode="Markdown"
        )
        
    else:
        bot.send_message(
            message.chat.id, 
            "Пожалуйста, используйте кнопки меню внизу экрана."
        )

if __name__ == '__main__':
    print("Бот SofiTours успешно запущен! Нажмите Ctrl+C для остановки.")
    bot.polling(none_stop=True)
