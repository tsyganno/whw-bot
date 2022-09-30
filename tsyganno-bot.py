import logging
import sqlite3
import os
import time
import requests
from aiogram import Bot, Dispatcher, types, executor
from bs4 import BeautifulSoup
from deepface import DeepFace
from pyowm import OWM
from pyowm.commons import exceptions
from transliterate import translit


sign_of_horoscope = [
    'Овен',
    'Телец',
    'Близнецы',
    'Рак',
    'Лев',
    'Дева',
    'Весы',
    'Скорпион',
    'Стрелец',
    'Козерог',
    'Водолей',
    'Рыбы'
]
example_cities = [
    'Москва',
    'Санкт-Петербург',
    'Иркутск',
    'Улан-Удэ',
    'Новосибирск',
    'Краснодар'
]


API_TOKEN = 'key'
owm = OWM('key_owm')

mgr = owm.weather_manager()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


conn = sqlite3.connect('bd/database.db', check_same_thread=False)
cursor = conn.cursor()


def get_horoscope(answer):
    """ Возвращает текст гороскопа по знаку зодиака парсингом кода страницы html"""
    link = 'https://retrofm.ru/index.php?go=goroskop'
    inquiry = requests.get(link)
    soup = BeautifulSoup(inquiry.text, 'html.parser')
    my_list_1 = soup.find_all("div", {"class": "text_box"})
    for el in my_list_1:
        element = str(el).strip()
        if answer in element:
            index_1 = element.find(f'<h6>{answer}</h6>') + len(answer) + 9
            index_2 = element.find('</div>') - 5
            return element[index_1: index_2].strip()
    return 'К сожалению, на данный момент астрологи еще не составили Гороскоп для вас =('


def city_weather(human_message):
    """ Производим транслитерацию с русского языка на английский,
    пытаемся получить данные погодных условий по переданному названию города"""
    city = translit(human_message, "ru", reversed=True) + ', RU'
    try:
        observation = mgr.weather_at_place(city)
    except exceptions.NotFoundError:
        return None
    return observation.weather.temperature('celsius')


def keyboard_sign_of_horoscope():
    keyboard = types.ReplyKeyboardMarkup(row_width=3)
    sign_buttons = []
    for sign in sign_of_horoscope:
        sign_buttons.append(types.KeyboardButton(sign))
    keyboard.add(*sign_buttons, types.KeyboardButton('/Назад'))
    return keyboard


def keyboard_cities():
    """ Создаем клавиатуру в меню диалога с названиями городов и клавишу 'Назад'"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    city_buttons = []
    for city in example_cities:
        city_buttons.append(types.KeyboardButton(city))
    keyboard.add(*city_buttons, types.KeyboardButton('/Назад'))
    return keyboard


def db_table_val(user_id: int, user_name: str, user_surname: str, username: str, time_user: str, message: str, photo: str):
    cursor.execute(
        'INSERT INTO data (user_id, user_name, user_surname, username, time_user, message, photo) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            user_id,
            user_name,
            user_surname,
            username,
            time_user,
            message,
            photo
        )
    )
    conn.commit()


def face_analyze(image_path):

    try:
        result_dict = DeepFace.analyze(
            img_path=image_path,
            actions=['age', 'gender', 'race', 'emotion']
        )

        data_dict = {
            'Age': result_dict.get("age"),
            'Gender': result_dict.get("gender"),
        }

        for k, v in result_dict.get('race').items():
            if 'Race' not in data_dict:
                if k == 'asian':
                    data_dict['Race'] = [f'Азия - {round(v, 2)}%']
                elif k == 'indian':
                    data_dict['Race'] = [f'Индия - {round(v, 2)}%']
                elif k == 'black':
                    data_dict['Race'] = [f'Африка - {round(v, 2)}%']
                elif k == 'white':
                    data_dict['Race'] = [f'Европа - {round(v, 2)}%']
                elif k == 'middle eastern':
                    data_dict['Race'] = [f'Ближний Восток - {round(v, 2)}%']
                elif k == 'latino hispanic':
                    data_dict['Race'] = [f'Испания (Латинская Америка) - {round(v, 2)}%']
            else:
                if k == 'asian':
                    data_dict['Race'].append(f'Азия - {round(v, 2)}%')
                elif k == 'indian':
                    data_dict['Race'].append(f'Индия - {round(v, 2)}%')
                elif k == 'black':
                    data_dict['Race'].append(f'Африка - {round(v, 2)}%')
                elif k == 'white':
                    data_dict['Race'].append(f'Европа - {round(v, 2)}%')
                elif k == 'middle eastern':
                    data_dict['Race'].append(f'Ближний Восток - {round(v, 2)}%')
                elif k == 'latino hispanic':
                    data_dict['Race'].append(f'Испания (Латинская Америка) - {round(v, 2)}%')

        for k, v in result_dict.get('emotion').items():
            if 'Emotions' not in data_dict:
                if k == 'angry':
                    data_dict['Emotions'] = [f'Гнев - {round(v, 2)}%']
                elif k == 'disgust':
                    data_dict['Emotions'] = [f'Отвращение - {round(v, 2)}%']
                elif k == 'fear':
                    data_dict['Emotions'] = [f'Страх - {round(v, 2)}%']
                elif k == 'happy':
                    data_dict['Emotions'] = [f'Счастье - {round(v, 2)}%']
                elif k == 'sad':
                    data_dict['Emotions'] = [f'Печаль - {round(v, 2)}%']
                elif k == 'surprise':
                    data_dict['Emotions'] = [f'Удивление - {round(v, 2)}%']
                elif k == 'neutral':
                    data_dict['Emotions'] = [f'Нейтральность - {round(v, 2)}%']
            else:
                if k == 'angry':
                    data_dict['Emotions'].append(f'Гнев - {round(v, 2)}%')
                elif k == 'disgust':
                    data_dict['Emotions'].append(f'Отвращение - {round(v, 2)}%')
                elif k == 'fear':
                    data_dict['Emotions'].append(f'Страх - {round(v, 2)}%')
                elif k == 'happy':
                    data_dict['Emotions'].append(f'Счастье - {round(v, 2)}%')
                elif k == 'sad':
                    data_dict['Emotions'].append(f'Печаль - {round(v, 2)}%')
                elif k == 'surprise':
                    data_dict['Emotions'].append(f'Удивление - {round(v, 2)}%')
                elif k == 'neutral':
                    data_dict['Emotions'].append(f'Нейтральность - {round(v, 2)}%')

        return data_dict

    except Exception:
        return 'Вы прикрепили некорректное фото (на фото должно быть лицо крупным планом).'


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=3,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    button_1 = types.KeyboardButton('/Погода')
    button_2 = types.KeyboardButton('/Гороскоп')
    button_3 = types.KeyboardButton('/Пожелание')
    keyboard.add(
        button_1,
        button_2,
        button_3
    )
    await message.reply('Привет, меня зовут Йозеф, и я телеграм-бот :)\n '
                        'Загрузи свою фотку или фотку друга, чье описание ты хочешь получить... \n '
                        'Узнай погоду в своем городе, ну или свой гороскоп по знаку зодиака =)',
                        reply_markup=keyboard)


@dp.message_handler(commands=['Погода'])
async def echo(message: types.Message):
    await message.answer(
        'Введите название города, который вас интересует =)',
        reply_markup=keyboard_cities()
    )


@dp.message_handler(commands=['Гороскоп'])
async def echo(message: types.Message):
    await message.answer(
        'Введите свой знак зодиака =)',
        reply_markup=keyboard_sign_of_horoscope()
    )


@dp.message_handler(commands=['Назад'])
async def echo(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        row_width=3,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    button_1 = types.KeyboardButton('/Погода')
    button_2 = types.KeyboardButton('/Гороскоп')
    button_3 = types.KeyboardButton('/Пожелание')
    keyboard.add(
        button_1,
        button_2,
        button_3
    )
    await message.reply(
        'Ты вернулся в главное меню =)\nВыбери раздел: "Погода", "Гороскоп" на сегодня или "Пожелание".',
        reply_markup=keyboard
    )


@dp.message_handler()
async def echo(message: types.Message):
    incoming = str(message.text)
    human_message = incoming[0].upper() + incoming[1:]
    if human_message in sign_of_horoscope:
        await message.answer(get_horoscope(human_message))
    else:
        data = city_weather(human_message)
        if data is None:
            await message.answer('Введите корректные данные.')
        else:
            output_message = f'Температура сейчас: {data["temp"]}\nМаксимальная температура сегодня: ' \
                             f'{data["temp_max"]}\n'f'Минимальная температура сегодня: ' \
                             f'{data["temp_min"]}\nОщущается как: {data["feels_like"]}'
            await message.answer(output_message)
            await message.answer(
                'Введите название города, который вас интересует.',
                reply_markup=keyboard_cities()
            )


@dp.message_handler(content_types=['photo'])
async def scan_message(message: types.Message):
    time_user = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    message_user = message.text
    us_id = message.from_user.id
    us_name = message.from_user.first_name
    us_sname = message.from_user.last_name
    username = message.from_user.username

    if message.photo:

        """
        path_img = os.path.join('photos', str(username), message.photo[-1].file_unique_id + '.jpg')
        await message.photo[-1].download(destination_file=path_img)
        """

        document_id = message.photo[-1].file_id
        file_info = await bot.get_file(document_id)

        path = f'http://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
        answer = face_analyze(path)
        db_table_val(
            user_id=us_id,
            user_name=us_name,
            user_surname=us_sname,
            username=username,
            time_user=time_user,
            message=message_user,
            photo=path
        )
        if type(answer) == dict:
            word = ''
            for key, value in answer.items():
                if key == 'Race':
                    word += 'У вас обнаружены черты следующих народностей:' + '\n'
                    for el in value:
                        word += el + '\n'
                    word += '\n'
                elif key == 'Emotions':
                    word += 'У вас обнаружены следующие эмоции:' + '\n'
                    for el in value:
                        word += el + '\n'
                    word += '\n'
                elif key == 'Age':
                    word += 'Возраст:' + ' ' + str(value) + '\n' + '\n'
                elif key == 'Gender':
                    if value == 'Man':
                        word += 'Пол:' + ' ' + 'Мужчина' + '\n' + '\n'
                    else:
                        word += 'Пол:' + ' ' + 'Женщина' + '\n' + '\n'

            await message.answer(word)
        else:
            await message.answer(answer)
    else:
        db_table_val(
            user_id=us_id,
            user_name=us_name,
            user_surname=us_sname,
            username=username,
            time_user=time_user,
            message=message_user,
            photo='нет данных'
        )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
