import asyncio
import csv
import os
from datetime import datetime
import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_country = State()

def log_to_csv(message: types.Message, motion: str, api: str, answer: str):
    file_exists = os.path.isfile('log.csv')
    unic_id = 1
    if file_exists:
        with open('log.csv', 'r', encoding='utf-8') as f:
            unic_id = 0
            for line in f:
                unic_id += 1
    with open('log.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Unic_ID', '@TG_nick', 'Motion', 'API', 'Date', 'Time', 'API_answer'])
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M:%S')
        nick = f'@{message.from_user.username}' if message.from_user.username else 'no_nick'
        writer.writerow([unic_id, nick, motion, api, date_str, time_str, answer])

start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Старт')]],
    resize_keyboard=True
)

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Университеты')],
        [KeyboardButton(text='Интересный факт')],
        [KeyboardButton(text='Собачка')]
    ],
    resize_keyboard=True
)

@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    log_to_csv(message, 'Button click', 'NONE', 'SUCCESS')
    await message.answer('Нажми на кнопку "Старт", чтобы открыть меню', reply_markup=start_kb)

@dp.message(F.text == 'Старт')
async def main_menu(message: types.Message):
    log_to_csv(message, 'Button click', 'NONE', 'SUCCESS')
    await message.answer('Выберите нужный API:', reply_markup=menu_kb)

@dp.message(F.text == 'Собачка')
async def get_dog(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://dog.ceo/api/breeds/image/random') as resp:
            data = await resp.json()
            dog_url = data.get('message')
            await message.answer_photo(dog_url)
            log_to_csv(message, 'Button click', 'Dog API', 'SUCCESS')

@dp.message(F.text == 'Интересный факт')
async def get_fact(message: types.Message):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://uselessfacts.jsph.pl/api/v2/facts/random') as resp:
            data = await resp.json()
            fact_text = data.get('text')
            await message.answer(f'Интересный факт: {fact_text}')
            log_to_csv(message, 'Button click', 'Facts API', 'SUCCESS')

@dp.message(F.text == 'Университеты')
async def ask_country(message: types.Message, state: FSMContext):
    await message.answer('Введите название страны на английском (например, Russian Federation')
    await state.set_state(Form.waiting_for_country)
    log_to_csv(message, 'Button click', 'University API', 'WAITING_INPUT')

@dp.message(Form.waiting_for_country)
async def get_universities(message: types.Message, state: FSMContext):
    country = message.text
    async with aiohttp.ClientSession() as session:
        url = f'http://universities.hipolabs.com/search?country={country}'
        async with session.get(url) as resp:
            data = await resp.json()
            if data:
                names = [uni['name'] for uni in data[:10]]
                response_text = 'Список университетов:\n' + '\n'.join(names)
                await message.answer(response_text)
                log_to_csv(message, 'Keyboard typing', 'University API', 'SUCCESS')
            else:
                await message.answer('Ничего не найдено.')
                log_to_csv(message, 'Keyboard typing', 'University API', 'EMPTY_RESULT')
    await state.clear()

@dp.message()
async def unknown_message(message: types.Message):
    log_to_csv(message, 'Keyboard typing', 'NONE', 'NONE')
    await message.answer(f'Вы написали: "{message.text}", я не знаю такой команды.')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
