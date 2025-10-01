from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardButton, InlineKeyboardMarkup)

register = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Создать профиль!')]],
                               resize_keyboard=True,
                               input_field_placeholder='Пройдите регистрацию...')

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📋 Посмотреть профиль')],
                                     [KeyboardButton(text='➕ Добавить квест')],
                                     [KeyboardButton(text='📜 Мои квесты')],
                                     [KeyboardButton(text='🛠️ Распределить очки')]],
                           resize_keyboard=True
                           )

complete_main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='✅ Выполнить квест')],
                                              [KeyboardButton(text='📋 Посмотреть профиль')],
                                              [KeyboardButton(text='➕ Добавить квест')]],
                                    resize_keyboard=True
                                    )

categories = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Интеллект 🧠', callback_data='intelligence')],
                     [InlineKeyboardButton(text='Сила 💪', callback_data='strength')]]
    )

stats = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Интеллект 🧠', callback_data='stat_intelligence')],
                     [InlineKeyboardButton(text='Сила 💪', callback_data='stat_strength')]]
    )
