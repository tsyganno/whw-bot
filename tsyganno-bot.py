import logging
from aiogram import Bot, Dispatcher, types, executor
from deepface import DeepFace


API_TOKEN = 'key'


logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


def face_analyze(image_path):

    try:
        result_dict = DeepFace.analyze(img_path=image_path, actions=['age', 'gender', 'race', 'emotion'])

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
    await message.reply('Привет, меня зовут Йозеф, и я телеграм-бот =)\n '
                        'Загрузи свою фотку или фотку друга, чье описание ты хочешь получить... =)')


@dp.message_handler(content_types=['photo'])
async def scan_message(message: types.Message):
    document_id = message.photo[0].file_id
    file_info = await bot.get_file(document_id)
    path = f'http://api.telegram.org/file/bot{API_TOKEN}/{file_info.file_path}'
    answer = face_analyze(path)
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
