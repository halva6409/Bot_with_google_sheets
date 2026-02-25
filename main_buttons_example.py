"""
Пример использования двух inline-кнопок с pyTelegramBotAPI (telebot).
Файл не меняет ваш `main.py` — это отдельный пример.

Инструкции:
1) Убедитесь, что в `secret.py` есть переменная `TOKEN`.
2) Установите библиотеку: pip install pyTelegramBotAPI
3) Запустите: python main_buttons_example.py

Кнопки: две inline-кнопки: "Кнопка A" и "Кнопка B".
При нажатии бот отвечает callback-ответом и редактирует сообщение.
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Берём токен из secret.py (файл уже есть в проекте)
from secret import TOKEN

bot = telebot.TeleBot(TOKEN)

# Функция-обертка для создания клавиатуры с двумя inline-кнопками
def build_inline_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)

    # Каждая кнопка имеет текст и callback_data — уникальную строку, по которой
    # мы будем распознавать, какую кнопку нажали.
    btn_a = InlineKeyboardButton(text='Кнопка A', callback_data='btn_a')
    btn_b = InlineKeyboardButton(text='Кнопка B', callback_data='btn_b')

    keyboard.add(btn_a, btn_b)
    return keyboard


# Обработчик команды /start — отправляет сообщение с inline-кнопками
@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Отправляет сообщение с двумя inline-кнопками."""
    kb = build_inline_keyboard()
    bot.send_message(message.chat.id, 'Выберите кнопку:', reply_markup=kb)


# Callback query handler — срабатывает при нажатии inline-кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """
    Здесь мы проверяем call.data и реагируем в зависимости от нажатой кнопки.
    Пример прост: бот отправляет короткий ответ (alert=False) и редактирует
    исходное сообщение, чтобы показать, какая кнопка была нажата.
    """
    if call.data == 'btn_a':
        # Ответ без всплывающего окна (show_alert=False), просто уведомление
        bot.answer_callback_query(call.id, text='Нажата Кнопка A', show_alert=False)

        # Можно редактировать исходный текст сообщения
        bot.edit_message_text('Вы выбрали: Кнопка A', chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

    elif call.data == 'btn_b':
        bot.answer_callback_query(call.id, text='Нажата Кнопка B', show_alert=False)
        bot.edit_message_text('Вы выбрали: Кнопка B', chat_id=call.message.chat.id,
                              message_id=call.message.message_id)

    else:
        bot.answer_callback_query(call.id, text='Неизвестная кнопка', show_alert=False)


if __name__ == '__main__':
    # Запускаем бота в режиме polling
    print('Запускаю пример бота с inline-кнопками. Отправьте /start в чате.')
    bot.polling(none_stop=True)
