import copy
import json
import logging
import random
import sqlite3
from flask import Flask, request, render_template
from portrait import portraits, hash_pass, unhash_pass

# не удаляйте этот путь т.к. у меня проблема с открытием data.json
# with open('C:/Users/Daniel/dev/github/alice-skills/Data.json', encoding='utf8') as f:
# альтернатива для вас:
with open('Data.json', encoding='utf8') as f:
    data = json.loads(f.read())['test']  # массив из словарей дат
with open('Data.json', encoding='utf8') as f:
    terms = json.loads(f.read())['terms']  # same из терминов

app = Flask(__name__)
logging.basicConfig(
    filename='example.log',
    format='%(asctime)s %(name)s %(message)s',
    level=logging.INFO
)

sessionStorage = {}
x = hash_pass('Hello')
# print(x)
# print(unhash_pass(x, 'Hello'))

# реакции для более живого разговора
right = ['Отлично!', 'Правильно!', 'Супер!', 'Точно!', 'Верно!', 'Хорошо!', 'Неплохо!']

wrong = ['Ой!', 'Не то!', 'Ты ошибся!', 'Немного не то!', 'Неверно!', 'Неправильно!', 'Ошибочка!']

_next = ['Далее', 'Следующий вопрос', 'Продолжим', 'Следующее']

wtf = ['Прости, не понимаю тебя', 'Можешь повторить, пожалуйста?', 'Повтори, пожалуйста', 'Прости, не слышу тебя']

goodbye = ['Пока!', 'До встречи!', 'Будем на связи!', 'Рада была пообщаться!', 'Пока-пока!']

hey = ['Привет', 'Приветствую тебя', 'Отличный день сегодня', 'Хорошо, что мы снова встретились', 'Приветик',
       'Здравствуй']


def config(user_id):
    # перемешивание дат и терминов
    arr = copy.deepcopy(data)
    term = copy.deepcopy(terms)
    random.shuffle(arr)
    random.shuffle(term)
    sessionStorage[user_id] = {
        'suggests': [
            "Даты 🕰",
            "Картины 🌄",
            "Термины 📚",
            "Ресурсы 📎",
            "Рейтинг 🏆",
            "Закрыть навык ❌"
        ],
        'slicedsuggests': [
            "Закрыть навык ❌",
            "Меню"
        ],
        "nick": None,
        'id': 0,
        'mode': '',
        'lastPic': False,
        # переменные для дат
        'test': arr,
        'lastQ': False,

        # очки для БД
        'test_count': 0,
        'pic_count': 0,
        'ter_count': 0,

        # переменные для терминов
        'term': term,
        'lastT': False,
        'terID': 0
    }


def write_in_base(user_id):
    con = sqlite3.connect("users.db")
    cur = con.cursor()  # Вот тут будем заносить данные в БД
    test_count = sessionStorage[user_id]['test_count']
    pic_count = sessionStorage[user_id]['pic_count']
    ter_count = sessionStorage[user_id]['ter_count']
    cur.execute(f"SELECT * FROM u WHERE nick = '{sessionStorage[user_id]['nick']}';")
    if cur.fetchone() is None:
        id_ = len(cur.execute("SELECT * FROM u").fetchall())
        cur.execute("INSERT INTO u VALUES (?,?,?,?,?,?);",
                    (
                        id_ + 1,
                        sessionStorage[user_id]['nick'],  # Заглушка для имени
                        test_count,
                        pic_count,
                        ter_count,
                        test_count + pic_count + ter_count
                    )
                    )
    else:
        cur.execute("UPDATE u SET (date_count, pic_count, ter_count, summa) = (?,?,?,?) WHERE nick = ?;",
                    (
                        test_count,
                        pic_count,
                        ter_count,
                        test_count + pic_count + ter_count,
                        sessionStorage[user_id]['nick']
                    )
                    )
    con.commit()


@app.route('/records')
def records():
    con = sqlite3.connect("users.db")
    cur = con.cursor()
    persons = cur.execute("SELECT * FROM u").fetchall()
    persons = sorted(persons, key=lambda x: -x[-1])
    return render_template('records.html', title='Рекорды | ЕГЭ', persons=persons)


@app.route('/post', methods=['POST'])
def main():
    logging.info('REQUEST: %r', request.json)
    logging.info('\n')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
    }
    if 'screen' in request.json['meta']['interfaces']:
        handle_dialog(request.json, response)
    # if not 'screen' in request.json['meta']['interfaces']:
    #     station_dialog(request.json, response)
    logging.info('RESPONSE: %r', request.json)
    logging.info('\n\n')

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
    if req['session']['new']:
        config(user_id)
        try:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            user = cur.execute(f"SELECT * FROM u WHERE nick = '{req['state']['user']['nick']}';").fetchone()

            res['response']['text'] = \
                f"{random.choice(hey)}, {req['state']['user']['nick']}! Продолжим тренировку! " \
                f"Твои очки:\nДаты: {user[2]}\nКартины: {user[3]}\nТермины: {user[4]}."
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            sessionStorage[user_id]['test_count'] = user[2]
            sessionStorage[user_id]['pic_count'] = user[3]
            sessionStorage[user_id]['ter_count'] = user[4]

            res['response']['buttons'] = [
                {'title': suggest, 'hide': False}
                for suggest in sessionStorage[user_id]['suggests'][:4]
            ]
            res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                               'url': 'https://alice-skills-1--t1logy.repl.co/records'})
            res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})

        except Exception:
            res['response']['text'] = 'Привет! Я помогу тебе подготовиться к ЕГЭ по истории ✨\n ' \
                                      'Напиши или скажи свой никнейм для сохранения результатов:'
        return

    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                  'У меня есть несколько режимов, просто нажми на кнопку 👇, чтобы выбрать их.' \
                                  'Не забывай, твои ответы влияют на место в рейтинге, будь внимателен! 😁'
        res['response']['buttons'] = [
            {'title': suggest, 'hide': False}
            for suggest in sessionStorage[user_id]['suggests'][:4]
        ]
        res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                           'url': 'https://alice-skills-1--t1logy.repl.co/records'})
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})

        return

    if 'меню' in req['request']['original_utterance'].lower() or \
            'рейтинг' in req['request']['original_utterance'].lower() or 'помощь' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'У меня есть несколько режимов, просто нажми на кнопку 👇, чтобы выбрать их. ' \
                                  'За каждый правильный ответ в любом режиме зачисляются очки, будь внимателен! 😁'
        sessionStorage[user_id]['lastQ'] = False
        sessionStorage[user_id]['lastPic'] = False
        sessionStorage[user_id]['lastT'] = False
        res['response']['buttons'] = [
            {'title': suggest, 'hide': False}
            for suggest in sessionStorage[user_id]['suggests'][:4]
        ]
        res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                           'url': 'https://alice-skills-1--t1logy.repl.co/records'})
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})
        return

        # ставим режим
    if 'ресурсы' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'ресурсы'

    if 'даты' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'случайные даты'

    if 'картины' in req['request']['original_utterance'].lower() or 'потреты' in req['request'][
        'original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'картины'

    if 'термины' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'термины'

    # если в нашем запросе 'закрыть' заканчиваем сессию
    if 'закрыть' in req['request']['original_utterance'].lower():
        write_in_base(user_id)
        res['response']['text'] = random.choice(
            goodbye) + '\nЕсли тебе понравилось, поставь нам звёздочки 👇. Спасибо :) И проверь своё место в рейтинге!'
        res['response']['buttons'] = [{
            'title': 'Звёздочки ⭐️',
            'hide': False,
            'url': 'https://dialogs.yandex.ru/store/skills/1424e7f5-ege-po-istorii'
        },
            {
                'title': 'Рейтинг 🏆',
                'hide': False,
                'url': 'https://alice-skills-1--t1logy.repl.co/records'
            }
        ]
        res['response']['end_session'] = True
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        # config(user_id) # на случай если захочет заново играть БЕЗ перезапуска навыка
        return

    if sessionStorage[user_id]['mode'] == 'случайные даты':
        if not sessionStorage[user_id]['lastQ']:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            user_answer = req['request']['command'].lower().split(' ')
            right_answer = sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer'].lower().split(
                ' ')

            print(right_answer)
            print(user_answer)
            if len(right_answer) > 1:  # если у нас 2 года
                if right_answer[0] in user_answer and right_answer[1] in user_answer:
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['test_count'] += 1  # Сохранение очков по датам
                    write_in_base(user_id)
                else:
                    res['response'][
                        'text'] = f"{random.choice(wrong)} Правильный ответ: в {right_answer[0]}-{right_answer[1]} гг. \n{random.choice(_next)}: {res['response']['text']}"
            else:  # если 1 год
                if right_answer[0] in user_answer:
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['test_count'] += 1
                    write_in_base(user_id)
                else:
                    res['response'][
                        'text'] = f"{random.choice(wrong)} Правильный ответ: в {right_answer[0]} г. \n{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['id'] += 1

    elif sessionStorage[user_id]['mode'] == 'картины':
        if not sessionStorage[user_id]['lastPic']:
            sessionStorage[user_id]['arrayPic'] = list(portraits)
            random.shuffle(sessionStorage[user_id]['arrayPic'])
            sessionStorage[user_id]['idPic'] = 0
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Кто изображен на фотографии?'
            res['response']['card']['image_id'] = \
                portraits.get(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic']])
            sessionStorage[user_id]['lastPic'] = True
        else:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            for ans in sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1].lower().split('/'):
                if ans in req['request']['original_utterance'].lower():
                    res['response']['card']['title'] = random.choice(right)
                    sessionStorage[user_id]['pic_count'] += 1  # Сохранение очков по картинкам
                    write_in_base(user_id)
                    break
            else:
                res['response']['card']['title'] \
                    = f"{random.choice(wrong)} Правильный ответ: {sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1]}."

            if sessionStorage[user_id]['idPic'] == len(sessionStorage[user_id]['arrayPic']):
                random.shuffle(sessionStorage[user_id]['arrayPic'])
                sessionStorage[user_id]['idPic'] = 0
            res['response']['card']['image_id'] = \
                portraits.get(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic']])
            res['response']['card']['title'] += ' Кто изображен на фотографии?'
        res['response']['text'] = res['response']['card']['title']
        sessionStorage[user_id]['idPic'] += 1

    elif sessionStorage[user_id]['mode'] == 'термины':
        if not sessionStorage[user_id]['lastT']:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            sessionStorage[user_id]['lastT'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            if req['request']['original_utterance'].lower() in sessionStorage[user_id]['term'][
                sessionStorage[user_id]['terID'] - 1]['answer'].lower():
                res['response']['text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                sessionStorage[user_id]['ter_count'] += 1  # Сохранение очков по терминам
                write_in_base(user_id)
            else:
                res['response'][
                    'text'] = f"{random.choice(wrong)} Правильный ответ: {sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1]['answer']}. \n{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['terID'] += 1
    elif sessionStorage[user_id]['mode'] == 'ресурсы':
        res['response']['text'] = 'Здесь мы публикуем интересные материалы. Послушаем музыку или почитаем статьи?'
        res['response']['buttons'] = [{
            'title': 'Статьи️ 📖',
            'hide': False,
        },
            {
                'title': 'Музыка 🎵',
                'hide': False,
            }
        ]
        if 'музыка' in req['request']['original_utterance'].lower() or 'музыку' in req['request'][
            'original_utterance'].lower():
            res['response']['tts'] = "Вот подборка интересной музыки"
            res['response']['card'] = {
                "type": "ItemsList",
                "header": {
                    "text": "Историческая музыка",
                },
                "items": [
                    {
                        "image_id": "937455/3a9025e4d08f2c295d85",
                        "title": "Хиты СССР",
                        "description": "Плейлист на Яндекс Музыке",
                        "button": {
                            "url":
                                'https://music.yandex.ru/users/sctnStudio/playlists/1002'
                        }
                    },
                    {
                        "image_id": "1521359/94ab576717d5217f7fdb",
                        "title": "Гимны стран мира",
                        "description": "Плейлист на Яндекс Музыке",
                        "button": {
                            "url": 'https://music.yandex.ru/users/sctnStudio/playlists/1004'
                        }
                    },
                    {
                        "image_id": "965417/aa2cbef4a55c41b57322",
                        "title": "Военные песни",
                        "description": "Плейлист на Яндекс Музыке",
                        "button": {
                            "url": 'https://music.yandex.ru/users/sctnStudio/playlists/1001'
                        }
                    }
                ]
            }
        if 'статьи' in req['request']['original_utterance'].lower():
            res['response']['tts'] = "Вот подборка классных исторических статей"
            res['response']['card'] = {
                "type": "ItemsList",
                "header": {
                    "text": "Полезные статьи",
                },
                "items": [
                    {
                        # "image_id": "937455/3a9025e4d08f2c295d85",
                        "title": "13 лучших книг по истории России",
                        "description": "Источник: Lifehacker.ru",
                        "button": {
                            "url": 'https://lifehacker.ru/knigi-po-istorii/'
                        }
                    },
                    {
                        # "image_id": "1521359/94ab576717d5217f7fdb",
                        "title": "Советы ЕГЭ по истории",
                        "description": "Источник: Учёба.ру",
                        "button": {
                            "url": 'https://www.ucheba.ru/for-abiturients/ege/articles/history'
                        }
                    },
                    {
                        # "image_id": "965417/aa2cbef4a55c41b57322",
                        "title": "Памятки и шпаргалки по истории",
                        "description": "Источник: historystepa.ru",
                        "button": {
                            "url": 'http://historystepa.ru/'
                        }
                    }
                ]
            }
    else:
        res['response']['buttons'] = [
            {'title': suggest, 'hide': False}
            for suggest in sessionStorage[user_id]['suggests'][:4]
        ]
        res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                           'url': 'https://alice-skills-1--t1logy.repl.co/records'})
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})
        res['response']['text'] = f"{random.choice(wtf)}\nВыбери вариант из предложенных :)"
        return

    res['response']['buttons'] = [
        {'title': suggest, 'hide': True}
        for suggest in sessionStorage[user_id]['slicedsuggests']
    ]


def station_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
    if req['session']['new']:
        config(user_id)
        try:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            user = cur.execute(f"SELECT * FROM u WHERE nick = '{req['state']['user']['nick']}';").fetchone()

            res['response']['text'] = \
                f"{random.choice(hey)}, {req['state']['user']['nick']}! Продолжим тренировку! В любой момент ты можешь " \
                f"сказать: закрыть, чтобы закончить наш разговор." \
                f"\nВ какой режим ты хочешь поиграть: даты или термины?"

            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            sessionStorage[user_id]['test_count'] = user[2]
            sessionStorage[user_id]['ter_count'] = user[4]

        except Exception:
            res['response']['text'] = 'Привет! Я помогу тебе подготовиться к ЕГЭ по истории ✨\n ' \
                                      'Скажи свой никнейм для сохранения:'
        return

    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        sessionStorage[user_id]['nick'] = req['request']['original_utterance'] + "#" + tag
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                  ' В какой режим ты хочешь поиграть: даты или термины?' \
                                  ' За каждый правильный ответ зачисляются очки, будь внимателен! В любой момент ты можешь закончить наш разговор: просто скажи закрыть'
        return
    if 'помощь' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request']['original_utterance'].lower() or 'меню' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'На устройствах без экрана у меня есть 2 режима: даты или термины. В какой режим поиграем?'
        sessionStorage[user_id]['lastQ'] = False
        sessionStorage[user_id]['lastT'] = False
    if 'даты' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'случайные даты'
    if 'термины' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'термины'
    if 'закрыть' in req['request']['original_utterance'].lower():
        write_in_base(user_id)
        res['response']['text'] = random.choice(
            goodbye) + '\nЕсли тебе понравилось, поставь нам звёздочки на сайте Диалогов. Спасибо :)'
        res['response']['end_session'] = True
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        # config(user_id) # на случай если захочет заново играть БЕЗ перезапуска навыка
        return

    if sessionStorage[user_id]['mode'] == 'случайные даты':
        if not sessionStorage[user_id]['lastQ']:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            user_answer = req['request']['command'].lower().split(' ')
            right_answer = sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer'].lower().split(
                ' ')
            if len(right_answer) > 1:  # если у нас 2 года
                if right_answer[0] in user_answer and right_answer[1] in user_answer:
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['test_count'] += 1  # Сохранение очков по датам
                    write_in_base(user_id)
                else:
                    res['response'][
                        'text'] = f"{random.choice(wrong)} Правильный ответ: в {right_answer[0]}-{right_answer[1]} гг. \n{random.choice(_next)}: {res['response']['text']}"
            else:  # если 1 год
                if right_answer[0] in user_answer:
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['test_count'] += 1
                    write_in_base(user_id)
                else:
                    res['response'][
                        'text'] = f"{random.choice(wrong)} Правильный ответ: в {right_answer[0]} г. \n{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['id'] += 1


    elif sessionStorage[user_id]['mode'] == 'термины':
        if not sessionStorage[user_id]['lastT']:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            sessionStorage[user_id]['lastT'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            if req['request']['original_utterance'].lower() in sessionStorage[user_id]['term'][
                sessionStorage[user_id]['terID'] - 1]['answer'].lower():
                res['response']['text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                sessionStorage[user_id]['ter_count'] += 1  # Сохранение очков по терминам
                write_in_base(user_id)
            else:
                res['response'][
                    'text'] = f"{random.choice(wrong)} Правильный ответ: {sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1]['answer']}. \n{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['terID'] += 1
    else:
      res['response']['text'] = 'На устройствах без экрана у меня есть 2 режима: даты или термины. В какой режим поиграем?'  

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
