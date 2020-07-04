import copy
import json
import logging
import random
from threading import Thread

import psycopg2
from flask import Flask, request, render_template

from portrait import portraits

with open('Data.json', encoding='utf8') as f:
    data = json.loads(f.read())['test']  # массив из словарей дат
with open('Data.json', encoding='utf8') as f:
    terms = json.loads(f.read())['terms']  # same из терминов
with open('Data.json', encoding='utf8') as f:
    facts = json.loads(f.read())['facts']  # same из фактов
with open('Data.json', encoding='utf8') as f:
    culture = json.loads(f.read())['culture']  # same из фактов
with open('Data.json', encoding='utf8') as f:
    war = json.loads(f.read())['ww2']  # same из вов

app = Flask('')
# from flask_ngrok import run_with_ngrok
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'alice'
# logging.basicConfig(
#     filename='example.log',
#     format='%(asctime)s %(name)s %(message)s',
#     level=logging.INFO
# )


# commiting
# schedule.every().hour.do(commiting)


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


sessionStorage = {}

# реакции для более живого разговора
right = ['Отлично!', 'Правильно!', 'Супер!', 'Точно!', 'Верно!', 'Хорошо!', 'Неплохо!']

wrong = ['Ой!', 'Не то!', 'Ты ошибся!', 'Немного не то!', 'Неверно!', 'Неправильно!', 'Ошибочка!']

_next = ['Далее', 'Следующий вопрос', 'Продолжим', 'Следующее']

wtf = ['Прости, не понимаю тебя', 'Можешь повторить, пожалуйста?', 'Повтори, пожалуйста', 'Прости, не слышу тебя']

goodbye = ['Пока!', 'До встречи!', 'Будем на связи!', 'Рада была пообщаться!', 'Пока-пока!']

hey = ['Привет', 'Приветствую тебя', 'Отличный день сегодня', 'Хорошо, что мы снова встретились', 'Приветик',
       'Здравствуй']

do_not_know = ["Жаль!",
               "Эх, жалко!",
               "Мы это исправим!",
               "Ничего, все ещё впереди!",
               "Потренируйся ещё немного!",
               "Попробуй в следующий раз!",
               "Практикой можно достичь совершенства!",
               "Эту тему стоит подучить.",
               "Запоминай!",
               "В следущий раз получится!",
               "Поднажми, все супер!",
               "Ничего, бывает :)",
               "Бывает :)",
               "Все окей :)",
               "Старайся!",
               "Тренируйся дальше!"]


# Функция для записи результатов в хранилище Алисы
def write_in_state(user_id):
    return {
        'nick': sessionStorage[user_id]['nick'],
        'test_count': sessionStorage[user_id]['test_count'],
        'pic_count': sessionStorage[user_id]['pic_count'],
        'ter_count': sessionStorage[user_id]['ter_count'],
        'cul_count': sessionStorage[user_id]['cul_count']
    }


# Конфигурация для новой сессии
def config(user_id):
    # перемешивание дат и терминов
    arr = copy.deepcopy(data)
    term = copy.deepcopy(terms)
    random.shuffle(arr)
    random.shuffle(term)
    sessionStorage[user_id] = {
        'suggests': [
            "Викторина 🎯",
            "Развлечения 🎮",
            "Полезное ✅"
        ],
        'slicedsuggests': [
            "Меню",
            "Не знаю 🤷‍️"
        ],
        'test_buttons': [
            "Даты ⌛️",
            "Картины 🏞",
            "Термины 📖",
            "Меню"
        ],
        'want_to_change_nick': False,
        'old_nick': '',
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
        'cul_count': 0,

        # переменные для терминов
        'term': term,
        'lastT': False,
        'terID': 0,

        # переменные для ВОВ
        'ww2_id': 0,

    }


# Запись в БД
def write_in_base(user_id):
    con = psycopg2.connect(user="cbbdrghpynreoq",
                           password="97ef09f2e8c1be408a28e5bcef9597dbd01dc8b75be2c364b540f3f1e1c51d7c",
                           host="ec2-54-75-246-118.eu-west-1.compute.amazonaws.com",
                           port="5432",
                           database="d7m2s796gtnbj0")
    cur = con.cursor()
    test_count = sessionStorage[user_id]['test_count']
    pic_count = sessionStorage[user_id]['pic_count']
    ter_count = sessionStorage[user_id]['ter_count']
    cul_count = sessionStorage[user_id]['cul_count']
    cur.execute(f"SELECT * FROM u WHERE nick = '{sessionStorage[user_id]['nick']}';")
    if cur.fetchone() is None:

        cur.execute(
            f"INSERT INTO u VALUES (DEFAULT,'{sessionStorage[user_id]['nick']}',{test_count},{pic_count},{ter_count},{cul_count},{test_count + pic_count + ter_count + cul_count});")
    else:
        cur.execute(
            f"UPDATE u SET (date_count, pic_count, ter_count, cul_count, summa) = ({test_count},{pic_count},{ter_count},{cul_count},{test_count + pic_count + ter_count + cul_count}) WHERE nick = '{sessionStorage[user_id]['nick']}';")
    con.commit()
    con.close()


@app.route('/')
def hi():
    return 'Hey, our app works!'


# Таблица рекордов, сортировка по сумме очков
@app.route('/records')
def records():
    con = psycopg2.connect(user="cbbdrghpynreoq",
                           password="97ef09f2e8c1be408a28e5bcef9597dbd01dc8b75be2c364b540f3f1e1c51d7c",
                           host="ec2-54-75-246-118.eu-west-1.compute.amazonaws.com",
                           port="5432",
                           database="d7m2s796gtnbj0")
    cur = con.cursor()
    cur.execute("SELECT * FROM u;")
    persons = cur.fetchall()
    con.commit()
    con.close()
    persons = sorted(persons, key=lambda x: -x[-1])
    return render_template('records.html', title='Рекорды | ЕГЭ', persons=persons)


@app.route('/post', methods=['POST'])
def main():
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        },
    }
    if 'screen' in request.json['meta']['interfaces']:
        handle_dialog(request.json, response)
    else:
        station_dialog(request.json, response)
    return json.dumps(response)


# Список для режима "Викторина"
def victorina_list():
    return {
        "type": "ItemsList",
        "header": {
            "text": "Викторина 🎯"
        },
        "items": [
            {
                "title": "Даты",
                "description": "В этом режиме я буду спрашивать, когда произошло то или иное событие. "
                               "За правильно названный век ты получаешь 0.5 балла, а за точную дату - 1 ",
                "button": {
                    "text": "Даты"
                }
            },
            {
                "title": "Картины",
                "description": "Здесь я покажу тебе портреты исторических личностей, а тебе нужно угадать, "
                               "кто на них изображён ",
                "button": {
                    "text": "Картины"
                }
            },
            {
                "title": "Культура",
                "description": "В данном режиме я спрошу у тебя о различных соборах и постройках",
                "button": {
                    "text": "Культура"
                }
            },
            {
                "title": "Термины",
                "description": "Возвращение любимого режима для подготовки к №4 ЕГЭ. Создан при поддержке проекта 'ЕГЭ близко'",
                "button": {
                    "text": "Термины"
                }
            }
        ]
    }


# Список для режима "Полезное"
def useful_list():
    return {
        "type": "ItemsList",
        "header": {
            "text": "Полезное ✅"
        },
        "items": [
            {
                "title": "Факты двух столиц",
                "description": "Узнай необычные факты о Москве и Санкт-Петербурге!",
                "button": {
                    "text": "Факты двух столиц"
                }
            },
            {
                "title": "Великая Отечественная война",
                "description": "Вся история великой войны",
                "button": {
                    "text": "Великая Отечественная война"
                }
            },
            {
                "title": "Проект \"ЕГЭ близко\"",
                "description": "Наш партнерский проект в ВКонтакте. Присоединяйтесь!",
                "button": {
                    "url": "https://vk.com/ege72"
                }
            }
        ]
    }


# Реакция Алисы на неверный ответ пользователя
def alice_reaction_to_dont_know_or_wrong_answer(user_answer):
    if 'не знаю' in user_answer or 'хз' in user_answer or 'не помню' in user_answer:
        return random.choice(do_not_know)
    return random.choice(wrong)


# Для устройств с экраном
def handle_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
    if req['session']['new']:
        config(user_id)
        # Попытка: пользователь заходит в навык не в первый раз
        try:
            # con = sqlite3.connect("users.db")
            # cur = con.cursor()
            # user = cur.execute(f"SELECT * FROM u WHERE nick = '{req['state']['user']['nick']}';").fetchone()
            if not 'cul_count' in req['state']['user']:
                sessionStorage[user_id]['cul_count'] = 0
            else:
                sessionStorage[user_id]['cul_count'] = req['state']['user']['cul_count']
            res['response']['text'] = f"{random.choice(hey)}, {req['state']['user']['nick']}! " \
                f"Продолжим тренировку! Твои очки:\nДаты: {req['state']['user']['test_count']}\n" \
                f"Картины: {req['state']['user']['pic_count']}\nТермины: {req['state']['user']['ter_count']}\n" \
                f"Культура: {sessionStorage[user_id]['cul_count']}"
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            sessionStorage[user_id]['test_count'] = req['state']['user']['test_count']
            sessionStorage[user_id]['pic_count'] = req['state']['user']['pic_count']
            sessionStorage[user_id]['ter_count'] = req['state']['user']['ter_count']
            res['response']['buttons'] = [
                {'title': suggest, 'hide': False}
                for suggest in sessionStorage[user_id]['suggests']
            ]
            res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                               'url': 'https://alice-skills-1--t1logy.repl.co/records'})
            res['response']['buttons'].append({'title': 'Уровень 💪🏻', 'hide': False})
            res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})

        except Exception:
            res['response']['card'] = {
                "type": "BigImage",
                "image_id": "1030494/24c5d25eff634432c3ef",
                "title": "Привет!",
                "description": 'Я помогу тебе подготовиться к ЕГЭ по истории ✨\n ''Напиши или скажи своё имя '
                               'или никнейм для сохранения результатов: '
            }
            res['response']['text'] = res['response']['card']['description']
        return

    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        if len(req['request']['original_utterance']) > 30:
            res['response']['text'] = 'Ваше имя или никнейм занимает больше 30 символов. Пожалуйста, исправьте.'
        else:
            new_nick = req['request']['original_utterance'] + "#" + tag
            if sessionStorage[user_id]['want_to_change_nick']:
                con = psycopg2.connect(user="cbbdrghpynreoq",
                                       password="97ef09f2e8c1be408a28e5bcef9597dbd01dc8b75be2c364b540f3f1e1c51d7c",
                                       host="ec2-54-75-246-118.eu-west-1.compute.amazonaws.com",
                                       port="5432",
                                       database="d7m2s796gtnbj0")
                cur = con.cursor()
                print(new_nick, sessionStorage[user_id]['nick'])
                cur.execute(f"UPDATE u SET nick = '{new_nick}' WHERE nick = '{sessionStorage[user_id]['nick']}'")
                con.commit()
                con.close()
                sessionStorage[user_id]['want_to_change_nick'] = False
            sessionStorage[user_id]['nick'] = new_nick
            # write_in_base(user_id)
            res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                      'У меня есть несколько режимов, просто нажми на кнопку 👇 или скажи, ' \
                                      'чтобы выбрать их.' \
                                      ' Не забывай, твои ответы влияют на место в рейтинге, будь внимателен! 😁'
            res['response']['buttons'] = [
                {'title': suggest, 'hide': False}
                for suggest in sessionStorage[user_id]['suggests']
            ]
            res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                               'url': 'https://alice-skills-1--t1logy.repl.co/records'})
            res['response']['buttons'].append({'title': 'Уровень 💪🏻', 'hide': False})
            res['user_state_update'] = {
                'nick': sessionStorage[user_id]['nick']
            }

        return

    if res['response']['end_session'] is True:
        write_in_base(user_id)
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
    # log
    # logging.info(f"------REQUEST COMMAND: {req['request']['original_utterance']} DEVICE: {req['meta']['client_id']}\n")

    # Меню
    if 'меню' in req['request']['original_utterance'].lower() or \
            'рейтинг' in req['request']['original_utterance'].lower() or 'помощь' in req['request'][
        'original_utterance'].lower() or 'что ты умеешь' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'У меня есть несколько режимов, просто нажми на кнопку 👇, чтобы выбрать их. ' \
                                  'Не забывай, твои ответы влияют на место в рейтинге, будь внимателен! 😁'
        res['response']['tts'] = res['response']['text'] + 'Если хочешь, чтобы я называла тебя по-другому, скажи ' \
                                                           'сменить имя или сменить ник '
        sessionStorage[user_id]['lastQ'] = False
        sessionStorage[user_id]['lastPic'] = False
        sessionStorage[user_id]['lastT'] = False
        sessionStorage[user_id]['mode'] = ''
        res['response']['buttons'] = [
            {'title': suggest, 'hide': False}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                           'url': 'https://alice-skills-1--t1logy.repl.co/records'})
        res['response']['buttons'].append({'title': 'Уровень 💪🏻', 'hide': False})
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})
        return

    # Для смены ника
    if 'сменить ник' in req['request']['original_utterance'].lower() or \
            'сменить имя' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['old_nick'] = sessionStorage[user_id]['nick']
        sessionStorage[user_id]['nick'] = None
        res['response']['text'] = 'Как я могу тебя называть?'
        sessionStorage[user_id]['want_to_change_nick'] = True
        return

    # ставим режим
    if 'развлечения' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'ресурсы'

    if 'викторина' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'викторина'
    if 'полезное' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'полезное'

    if 'уровень' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'уровень'

    if 'факты двух столиц' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'факты'
        sessionStorage[user_id]['factID'] = 0
        fact = copy.deepcopy(facts)
        random.shuffle(fact)
        sessionStorage[user_id]['facts'] = fact

    if 'великая отечественная война' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['ww2_id'] = 0
        ww2 = copy.deepcopy(war)
        sessionStorage[user_id]['ww2'] = ww2
        sessionStorage[user_id]['mode'] = 'война'

    # если в нашем запросе 'закрыть' заканчиваем сессию
    if 'закрыть' in req['request']['original_utterance'].lower():
        res['response']['text'] = random.choice(
            goodbye) + '\nЕсли тебе понравилось, поставь нам оценку 👇. Спасибо :)\nПроверь своё место в рейтинге!\n' \
                       'Возвращайся почаще, ведь только постоянная практика может привести к успеху!'
        res['response']['buttons'] = [{
            'title': 'Оценить ⭐️',
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
        # config(user_id) # на случай если захочет заново играть БЕЗ перезапуска навыка
        return

    if 'даты' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'даты'
    if 'картины' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'картины'
    if 'термины' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'термины'
    if 'культура' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'культура'
        sessionStorage[user_id]['cultID'] = 0
        sessionStorage[user_id]['lastС'] = False
        cult = copy.deepcopy(culture)
        random.shuffle(cult)
        sessionStorage[user_id]['culture'] = cult

    # Обработка каждого режима
    if sessionStorage[user_id]['mode'] == 'полезное':
        res['response']['card'] = useful_list()
        if 'полезное' in req['request']['original_utterance'].lower():
            res['response'][
                'text'] = 'Здесь находятся интересные факты о Москве и Санкт-Петербурге,' \
                          ' а так же история Великой Отечественной войны. Выбирай, что хочешь послушать.'
        else:
            res['response']['text'] = 'Не понимаю. Выбери, пожалуйста, вариант из предложенных! '
        return
    elif sessionStorage[user_id]['mode'] == 'викторина':
        res['response']['card'] = victorina_list()
        if 'викторина' in req['request']['original_utterance'].lower():
            res['response']['text'] = 'В викторине я предлагаю тебе поиграть в несколько режимов: ' \
                                      'даты, картины, культура и термины. В каждом режиме за ' \
                                      'правильные ответы будут зачисляться очки, будь внимателен!'
        else:
            res['response'][
                'text'] = 'Не понимаю. Выбери вариант из предложенных, пожалуйста!'
        return
    elif sessionStorage[user_id]['mode'] == 'даты':
        if not sessionStorage[user_id]['lastQ']:  # Обработка первого вопроса
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:  # остальные вопросы
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            user_answer = req['request']['command'].lower()
            right_answer = sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer'].lower().split(
                '/')
            years = right_answer[0].split(' ')
            centuries = right_answer[1].split(' ')

            print(years, centuries)
            print(user_answer)
            if 'век' not in user_answer:
                if len(years) > 1:  # если у нас 2 года
                    if years[0] in user_answer and years[1] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 1  # Сохранение очков по датам
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"с {years[0]} год по {years[1]} год. \n{random.choice(_next)}: {res['response']['text']}"
                    print(years[0] in user_answer, years[1] in user_answer)
                else:  # если 1 год
                    if years[0] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 1
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response'][
                            'text'] = f"{word} Правильный ответ: " \
                                      f"в {years[0]} году. \n{random.choice(_next)}: {res['response']['text']}"
            else:
                if len(centuries) == 2:  # один век + слово "век"
                    if centuries[0] in user_answer and centuries[1] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 0.5
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)

                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"в {centuries[0]}-ом веке \n{random.choice(_next)}: {res['response']['text']}"
                else:
                    if centuries[0] in user_answer and centuries[1] in user_answer and centuries[2] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 0.5
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"с {centuries[0]}-ый век по {centuries[1]}-ый век \n{random.choice(_next)}: {res['response']['text']}"

        sessionStorage[user_id]['id'] += 1
        if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['test']):
            sessionStorage[user_id]['id'] = 0
            random.shuffle(sessionStorage[user_id]['test'])
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]

    elif sessionStorage[user_id]['mode'] == 'картины':
        if not sessionStorage[user_id]['lastPic']:  # Первый вопрос
            sessionStorage[user_id]['arrayPic'] = list(portraits)
            random.shuffle(sessionStorage[user_id]['arrayPic'])
            sessionStorage[user_id]['idPic'] = 0
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Кто изображен на фотографии?'
            res['response']['card']['image_id'] = \
                portraits.get(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic']])
            res['response']['text'] = 'Кто изображен на фотографии?'
            sessionStorage[user_id]['lastPic'] = True
        else:  # Остальные
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            for ans in sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1].lower().split('/'):
                if ans in req['request']['original_utterance'].lower():
                    res['response']['card']['title'] = random.choice(right)
                    sessionStorage[user_id]['pic_count'] += 1  # Сохранение очков по картинкам
                    res['user_state_update'] = write_in_state(user_id)
                    write_in_base(user_id)
                    break
                else:
                    word = alice_reaction_to_dont_know_or_wrong_answer(req['request']['original_utterance'].lower())
                    res['response']['card']['title'] \
                        = f"{word} Правильный ответ: " \
                          f"{random.choice(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1].split('/'))}."

            if sessionStorage[user_id]['idPic'] == len(sessionStorage[user_id]['arrayPic']):
                random.shuffle(sessionStorage[user_id]['arrayPic'])
                sessionStorage[user_id]['idPic'] = 0
            res['response']['card']['image_id'] = \
                portraits.get(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic']])
            res['response']['card']['title'] += ' Кто изображен на фотографии?'
            res['response']['text'] = res['response']['card']['title']
        sessionStorage[user_id]['idPic'] += 1
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]
    elif sessionStorage[user_id]['mode'] == 'термины':
        if not sessionStorage[user_id]['lastT']:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            sessionStorage[user_id]['lastT'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            for ans in sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1][
                'answer'].lower().split('/'):
                if ans in req['request']['original_utterance'].lower():
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['ter_count'] += 1  # Сохранение очков по терминам
                    res['user_state_update'] = write_in_state(user_id)
                    write_in_base(user_id)
                    break
            else:
                word = alice_reaction_to_dont_know_or_wrong_answer(req['request']['original_utterance'].lower())
                res['response'][
                    'text'] = f"{word} Правильный ответ: " \
                    f"{sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1]['answer']}. \n" \
                    f"{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['terID'] += 1
        if sessionStorage[user_id]['terID'] == len(sessionStorage[user_id]['term']):
            random.shuffle(sessionStorage[user_id]['term'])
            sessionStorage[user_id]['terID'] = 0
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]
    elif sessionStorage[user_id]['mode'] == 'культура':
        if not sessionStorage[user_id]['lastС']:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID']][
                'question']
            res['response']['card']['image_id'] = sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID']][
                'photo_id']
            sessionStorage[user_id]['lastС'] = True
        else:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'

            res['response']['card']['image_id'] = sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID']][
                'photo_id']
            res['response']['text'] = sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID']]['question']
            for ans in sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID'] - 1][
                'answer'].lower().split('/'):
                if ans in req['request']['original_utterance'].lower():
                    res['response']['card'][
                        'title'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['cul_count'] += 1  # Сохранение очков по терминам
                    res['user_state_update'] = write_in_state(user_id)
                    write_in_base(user_id)
                    break
            else:
                word = alice_reaction_to_dont_know_or_wrong_answer(req['request']['original_utterance'].lower())
                res['response']['card']['title'] = f"{word} Правильный ответ: " \
                                                   f"{random.choice(sessionStorage[user_id]['culture'][sessionStorage[user_id]['cultID'] - 1]['answer'].split('/'))}. \n" \
                                                   f"{random.choice(_next)}: {res['response']['text']}"
        res['response']['text'] = res['response']['card']['title']
        sessionStorage[user_id]['cultID'] += 1
        if sessionStorage[user_id]['cultID'] == len(sessionStorage[user_id]['culture']):
            random.shuffle(sessionStorage[user_id]['culture'])
            sessionStorage[user_id]['cultID'] = 0
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests']
        ]

    elif sessionStorage[user_id]['mode'] == 'ресурсы':

        if 'развлечения' in req['request']['original_utterance'].lower():
            res['response']['buttons'] = [{
                'title': 'Статьи️ 📖',
                'hide': True,
            },
                {
                    'title': 'Музыка 🎵',
                    'hide': True,
                }
            ]
            res['response']['text'] = 'Здесь мы публикуем интересные материалы. Послушаем музыку или почитаем статьи?'
        elif 'музыка' in req['request']['original_utterance'].lower() or 'музыку' in req['request'][
            'original_utterance'].lower():
            res['response']['buttons'] = [{
                'title': 'Статьи️ 📖',
                'hide': True,
            }]
            res['response']['tts'] = "Вот подборка интересной музыки"
            res['response']['text'] = res['response']['tts']
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
        elif 'статьи' in req['request']['original_utterance'].lower():
            res['response']['buttons'] = [
                {
                    'title': 'Музыка 🎵',
                    'hide': True,
                }
            ]
            res['response']['tts'] = "Вот подборка классных исторических статей"
            res['response']['text'] = res['response']['tts']
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
            res['response']['buttons'] = [{
                'title': 'Статьи️ 📖',
                'hide': True,
            },
                {
                    'title': 'Музыка 🎵',
                    'hide': True,
                }
            ]
            res['response']['text'] = f"{random.choice(wtf)}\nВыбери вариант из предложенных, пожалуйста!"
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': True})
        res['response']['buttons'].append({'title': 'Меню', 'hide': True})
        res['response']['buttons'].append({'title': 'Оценить ⭐', 'hide': True,
                                           'url': 'https://dialogs.yandex.ru/store/skills/1424e7f5-ege-po-istorii'})
        return
    elif sessionStorage[user_id]['mode'] == 'уровень':
        test_count = sessionStorage[user_id]['test_count']
        pic_count = sessionStorage[user_id]['pic_count']
        ter_count = sessionStorage[user_id]['ter_count']
        cul_count = sessionStorage[user_id]['cul_count']
        summa = test_count + pic_count + ter_count + cul_count
        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['tts'] = '<speaker audio="alice-sounds-game-win-1.opus">'
        if summa < 20:
            res['response']['text'] = f'Ты еще новичок, 1 уровень! ' \
                                      f'Поднажми: до 2ого уровня осталось {20 - summa} {count_naming(20, summa)}'
            res['response']['card']['image_id'] = '1540737/62bffa1f1c62a4c6812c'
        elif summa < 40:
            res['response']['text'] = f'Круто! 2 уровень. Рекомендую поднажать:' \
                                      f' до 3ого уровня осталось {40 - summa} {count_naming(40, summa)}'
            res['response']['card']['image_id'] = '213044/e3649e3e18880a531e76'
        elif summa < 60:
            res['response']['text'] = f'Ого! Ты на третьем уровне. Совсем чуть-чуть до победы, осталось ' \
                                      f'{60 - summa} {count_naming(60, summa)}'
            res['response']['card']['image_id'] = '1652229/aadaf325e34cb47c7401'
        else:
            res['response']['text'] = f'Поздравляю! С уверенностью могу назвать тебя настоящим историком!'
            res['response']['card']['image_id'] = '1540737/674b982eaca1f8245da4'
        res['response']['card']['title'] = res['response']['text']
        res['response']['tts'] += res['response']['text']
        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['slicedsuggests'][:1]
        ]

        res['response']['buttons'].append({'title': 'Оценить ⭐', 'hide': True,
                                           'url': 'https://dialogs.yandex.ru/store/skills/1424e7f5-ege-po-istorii'})
        return

    elif sessionStorage[user_id]['mode'] == 'факты':
        res['response']['buttons'] = []
        res['response']['text'] = sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']]['fact']
        res['response']['tts'] = sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']]['tts']
        if 'photo_id' in sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']]:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']][
                'title']
            res['response']['card']['image_id'] = sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']][
                'photo_id']
        sessionStorage[user_id]['factID'] += 1
        if sessionStorage[user_id]['factID'] == len(facts):
            sessionStorage[user_id]['factID'] = 0
            res['response']['text'] += '\nНаши факты закончились! Переходи в другие режимы, будет весело!'
        else:
            res['response']['buttons'].append({'title': 'Дальше', 'hide': True})
        res['response']['buttons'].append({'title': 'Меню', 'hide': True})

    elif sessionStorage[user_id]['mode'] == 'война':
        res['response']['buttons'] = []
        if 'назад' in req['request']['original_utterance'].lower():
            sessionStorage[user_id]['ww2_id'] -= 1
        if 'далее' in req['request']['original_utterance'].lower():
            sessionStorage[user_id]['ww2_id'] += 1
        res['response']['text'] = sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['text']
        if sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['tts'] != '':
            res['response']['tts'] = sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['tts']
        if sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['pic_id'] != '':
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']][
                'title']
            res['response']['card']['image_id'] = \
                sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']][
                    'pic_id']
        if sessionStorage[user_id]['ww2_id'] == len(sessionStorage[user_id]['ww2']) - 1:
            res['response']['buttons'] = []
            res['response']['text'] += 'История войны закончилась. Переходи в другие режимы'
            res['response']['buttons'] = [
                {'title': 'Назад', 'hide': True},
                {'title': 'Меню', 'hide': True},
            ]
            return
        if sessionStorage[user_id]['ww2_id'] == 0:
            res['response']['buttons'] = []
            res['response']['buttons'] = [
                {'title': 'Далее', 'hide': True},
                {'title': 'Меню', 'hide': True},
            ]
            return

        res['response']['buttons'] = [
            {'title': 'Назад', 'hide': True},
            {'title': 'Далее', 'hide': True},
            {'title': 'Меню', 'hide': True},
        ]
    else:
        res['response']['buttons'] = [
            {'title': suggest, 'hide': False}
            for suggest in sessionStorage[user_id]['suggests'][:3]
        ]
        res['response']['buttons'].append({'title': 'Рейтинг 🏆', 'hide': False,
                                           'url': 'https://alice-skills-1--t1logy.repl.co/records'})
        res['response']['buttons'].append({'title': 'Уровень 💪🏻', 'hide': False})
        res['response']['buttons'].append({'title': 'Закрыть навык ❌', 'hide': False})
        res['response']['text'] = f"{random.choice(wtf)}\nВыбери вариант из предложенных :)"
    return


# Функция для верного произношения слова "очков" в режиме "Уровень"
def count_naming(level, summa):
    if level - summa >= 1:
        return 'очко'
    if 2 <= level - summa < 5:
        return 'очка'
    if 5 <= level - summa <= 20:
        return 'очков'


# Функция для устройств без экрана (Я.Станция, Я.Навигатор)
def station_dialog(req, res):
    user_id = req['session']['user_id']
    if res['response']['end_session'] is True:
        write_in_base(user_id)
    if req['session']['new']:
        config(user_id)
        try:
            # con = sqlite3.connect("users.db")
            # cur = con.cursor()
            # user = cur.execute(f"SELECT * FROM u WHERE nick = '{req['state']['user']['nick']}';").fetchone()
            if not 'cul_count' in req['state']['user']:
                sessionStorage[user_id]['cul_count'] = 0
            else:
                sessionStorage[user_id]['cul_count'] = req['state']['user']['cul_count']
            res['response']['text'] = \
                f"{random.choice(hey)}, {req['state']['user']['nick']}! Продолжим тренировку! " \
                f"Твои очки:\nДаты: {req['state']['user']['test_count']}\nКартины: {req['state']['user']['pic_count']}\n" \
                f"Культура: {sessionStorage[user_id]['cul_count']}\nВ " \
                f"какой режим ты хочешь сыграть: даты, термины или послушать интересные факты?"
            sessionStorage[user_id]['nick'] = req['state']['user']['nick']
            sessionStorage[user_id]['test_count'] = req['state']['user']['test_count']
            sessionStorage[user_id]['pic_count'] = req['state']['user']['pic_count']

        except Exception:
            res['response'][
                'text'] = 'Привет! Я помогу тебе подготовиться к ЕГЭ по истории, или просто освежить свои знания по истории. Так как у тебя устройство ' \
                          'без экрана или Навигатор, я могу предложить тебе только 4 режима. ' \
                          'Скажи своё имя для сохранения результатов:'
        return

    if sessionStorage[user_id]['nick'] is None:
        tag = str(random.randint(0, 10001))
        if len(req['request']['original_utterance']) > 30:
            res['response']['text'] = 'Ваше имя или никнейм занимает больше 30 символов. Пожалуйста, исправьте.'
        else:
            new_nick = req['request']['original_utterance'] + "#" + tag
            if sessionStorage[user_id]['want_to_change_nick']:
                con = psycopg2.connect(user="cbbdrghpynreoq",
                                       password="97ef09f2e8c1be408a28e5bcef9597dbd01dc8b75be2c364b540f3f1e1c51d7c",
                                       host="ec2-54-75-246-118.eu-west-1.compute.amazonaws.com",
                                       port="5432",
                                       database="d7m2s796gtnbj0")
                cur = con.cursor()
                print(new_nick, sessionStorage[user_id]['nick'])
                cur.execute(f"UPDATE u SET nick = '{new_nick}' WHERE nick = '{sessionStorage[user_id]['nick']}'")
                con.commit()
                con.close()
                sessionStorage[user_id]['want_to_change_nick'] = False
            sessionStorage[user_id]['nick'] = new_nick
        res['response']['text'] = f'Приятно познакомиться! Твой ник с тэгом: {sessionStorage[user_id]["nick"]}\n' \
                                  'У меня есть 4 режима: даты, где я буду спрашивать тебя о случайных исторических ' \
                                  'событиях, и война, где я расскажу тебе о Великой Отечественной войне. ' \
                                  'Режим термины позволит подготовиться к четвертому номеру в ЕГЭ.Или ты ' \
                                  'можешь послушать интересные исторические факты. Во что из этого поиграем? Если ты ' \
                                  'что-то пропустил, просто скажи: "помощь". '

        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        return
    if res['response']['end_session'] is True:
        write_in_base(user_id)
        res['user_state_update'] = {
            'nick': sessionStorage[user_id]['nick']
        }
        # config(user_id) # на случай если захочет заново играть БЕЗ перезапуска навыка
        return
    if 'даты' in req['request']['original_utterance'].lower() or 'да ты' in req['request']['original_utterance'].lower() \
            or 'дата' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'случайные даты'
    if 'термины' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'термины'
    if 'факты' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'факты'
        sessionStorage[user_id]['factID'] = 0
        fact = copy.deepcopy(facts)
        random.shuffle(fact)
        sessionStorage[user_id]['facts'] = fact
    if 'война' in req['request']['original_utterance'].lower() or 'войну' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['ww2_id'] = 0
        ww2 = copy.deepcopy(war)
        sessionStorage[user_id]['ww2'] = ww2
        sessionStorage[user_id]['mode'] = 'война'

    if 'помощь' in req['request']['original_utterance'].lower() or 'что ты умеешь' in req['request'][
        'original_utterance'].lower():
        res['response'][
            'text'] = 'У меня есть 4 режима: даты, где я буду спрашивать тебя о случайных исторических событиях, ' \
                      'и война, где я расскажу тебе о Великой Отечественной войне. ' \
                      'Режим термины позволит подготовиться к четвертому номеру в ЕГЭ. Или ты можешь послушать интересные ' \
                      'исторические факты. Во что из этого поиграем? '
        sessionStorage[user_id]['mode'] = ''
        return
    if sessionStorage[user_id]['mode'] == 'случайные даты':
        if not sessionStorage[user_id]['lastQ']:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            user_answer = req['request']['command'].lower()
            right_answer = sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer'].lower().split(
                '/')
            years = right_answer[0].split(' ')
            centuries = right_answer[1].split(' ')

            print(years, centuries)
            print(user_answer)
            if 'век' not in user_answer:
                if len(years) > 1:  # если у нас 2 года
                    if years[0] in user_answer and years[1] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 1  # Сохранение очков по датам
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"с {years[0]} год по {years[1]} год. \n{random.choice(_next)}: {res['response']['text']}"
                    print(years[0] in user_answer, years[1] in user_answer)
                else:  # если 1 год
                    if years[0] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 1
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response'][
                            'text'] = f"{word} Правильный ответ: " \
                                      f"в {years[0]} году. \n{random.choice(_next)}: {res['response']['text']}"
            else:
                if len(centuries) == 2:  # один век + слово "век"
                    if centuries[0] in user_answer and centuries[1] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 0.5
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)

                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"в {centuries[0]}-ом веке \n{random.choice(_next)}: {res['response']['text']}"
                else:
                    if centuries[0] in user_answer and centuries[1] in user_answer and centuries[2] in user_answer:
                        res['response'][
                            'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                        sessionStorage[user_id]['test_count'] += 0.5
                        res['user_state_update'] = write_in_state(user_id)
                        write_in_base(user_id)
                    else:
                        word = alice_reaction_to_dont_know_or_wrong_answer(user_answer)
                        res['response']['text'] = f"{word} Правильный ответ: " \
                                                  f"с {centuries[0]}-ый век по {centuries[1]}-ый век \n{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['id'] += 1
        if sessionStorage[user_id]['id'] == len(sessionStorage[user_id]['test']):
            sessionStorage[user_id]['id'] = 0
            random.shuffle(sessionStorage[user_id]['test'])

    elif sessionStorage[user_id]['mode'] == 'факты':
        res['response']['text'] = ''
        res['response']['tts'] = ''
        if sessionStorage[user_id]['factID'] == 0:
            res['response']['text'] = 'Чтобы перейти к следующему факту, скажи далее. '
        res['response']['text'] += sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']]['fact']
        res['response']['tts'] = sessionStorage[user_id]['facts'][sessionStorage[user_id]['factID']]['tts']
        sessionStorage[user_id]['factID'] += 1
        if sessionStorage[user_id]['factID'] == len(facts):
            sessionStorage[user_id]['factID'] = 0
            res['response']['text'] += '\nНаши факты закончились! Переходи в другие режимы, будет весело!'
            res['response']['tts'] = res['response']['text']
    elif sessionStorage[user_id]['mode'] == 'термины':
        if not sessionStorage[user_id]['lastT']:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            sessionStorage[user_id]['lastT'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['term'][sessionStorage[user_id]['terID']]['question']
            for ans in sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1][
                'answer'].lower().split(
                '/'):
                if ans in req['request']['original_utterance'].lower():
                    res['response'][
                        'text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
                    sessionStorage[user_id]['ter_count'] += 1  # Сохранение очков по терминам
                    res['user_state_update'] = write_in_state(user_id)
                    write_in_base(user_id)
                    break
            else:
                word = alice_reaction_to_dont_know_or_wrong_answer(req['request']['original_utterance'].lower())
                res['response'][
                    'text'] = f"{word} Правильный ответ: " \
                    f"{sessionStorage[user_id]['term'][sessionStorage[user_id]['terID'] - 1]['answer']}. \n" \
                    f"{random.choice(_next)}: {res['response']['text']}"
        sessionStorage[user_id]['terID'] += 1
        if sessionStorage[user_id]['terID'] == len(sessionStorage[user_id]['term']):
            random.shuffle(sessionStorage[user_id]['term'])
            sessionStorage[user_id]['terID'] = 0
    elif sessionStorage[user_id]['mode'] == 'война':
        res['response']['buttons'] = []
        if 'назад' in req['request']['original_utterance'].lower():
            sessionStorage[user_id]['ww2_id'] -= 1
        if 'далее' in req['request']['original_utterance'].lower():
            sessionStorage[user_id]['ww2_id'] += 1
        res['response']['text'] = sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['text']
        if sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['tts'] != '':
            res['response']['tts'] = sessionStorage[user_id]['ww2'][sessionStorage[user_id]['ww2_id']]['tts']
        if sessionStorage[user_id]['ww2_id'] == len(sessionStorage[user_id]['ww2']) - 1:
            res['response']['buttons'] = []
            res['response']['text'] += 'История войны закончилась. Переходи в другие режимы'
            res['response']['buttons'] = [
                {'title': 'Назад', 'hide': True},
                {'title': 'Меню', 'hide': True},
            ]
            return
        if sessionStorage[user_id]['ww2_id'] == 0:
            res['response']['buttons'] = []
            res['response']['buttons'] = [
                {'title': 'Далее', 'hide': True},
                {'title': 'Меню', 'hide': True},
            ]
            return
    else:
        res['response'][
            'text'] = f'В какой режим ты хочешь сыграть: даты, термины, войну или послушать интересные ' \
                      f'факты? '
    res['response']['buttons'] = [
        {'title': 'Помощь', 'hide': True}
    ]
    return


if __name__ == '__main__':
    #keep_alive()
    from flask_ngrok import run_with_ngrok
    run_with_ngrok(app)
    app.run()
    # app.run()
