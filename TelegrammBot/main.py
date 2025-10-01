import asyncio
import logging

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties

from config.config import TOKEN
from app.handlers import router

async def main():
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.include_router(router)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот успешно выключен')



#----------------------------------------------------------------------------------------------------------
#ctrl + c - Остановка программы
#ctrl + f - Поиск по элементу
#ctrl + alt + L - Форматирование по PEP8
#python main.py в терминале - запуск программы