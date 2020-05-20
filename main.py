import copy
import json
import logging
import random

from flask import Flask, request

from portrait import portraits

# не удаляйте этот путь т.к. у меня проблема с открытием data.json
# with open('C:/Users/Daniel/dev/github/alice-skills/Data.json', encoding='utf8') as f:
    # альтернатива для вас:
with open('Data.json', encoding='utf8') as f:
    data = json.loads(f.read())['test']  # массив из словарей

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}

# реакции для более живого разговора
right = ['Отлично!', 'Правильно!', 'Супер!', 'Точно!', 'Верно!', 'Хорошо!', 'Неплохо!']

wrong = ['Ой!', 'Не то!', 'Ты ошибся!', 'Немного не то!', 'Неверно!', 'Неправильно!', 'Ошибочка!']

_next = ['Далее', 'Следующий вопрос', 'Продолжим', 'Следующая дата']

wtf = ['Прости, не понимаю тебя', 'Можешь повторить, пожалуйста?', 'Повтори, пожалуйста', 'Прости, не слышу тебя']


@app.route('/', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    index()
    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def index():
    return "App works!"


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    # если 1 раз
    if req['session']['new']:
        arr = copy.deepcopy(data)
        random.shuffle(arr)  # перемешанная data
        sessionStorage[user_id] = {
            'suggests': [
                "Случайные даты",
                "Картины",
                "Закрыть ❌",
            ],
            'test': arr,
            'id': 0,
            'lastQ': False,
            'mode': '',
            'lastPic': False
        }
        res['response']['text'] = 'Привет! Я помогу тебе подготовиться к ЕГЭ по истории. ' \
                                  'Какой режим ты хочешь выбрать: случайные даты или портреты исторических личностей?'

        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        return
    # ставим режим

    if 'случайные даты' in req['request']['original_utterance'].lower():
        sessionStorage[user_id]['mode'] = 'случайные даты'

    if req['request']['original_utterance'].lower() == 'картины':
        sessionStorage[user_id]['mode'] = 'картины'
    else:
        res['response']['text'] = random.choice(wtf)

    if sessionStorage[user_id]['mode'] == 'случайные даты':
        if not sessionStorage[user_id]['lastQ']:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            print(sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question'])
            print(sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['answer'])
            print('моё ', req['request']['original_utterance'].lower())
            if sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1][
                'answer'].lower() in req['request']['original_utterance'].lower():
                res['response']['text'] = f"{random.choice(right)} {random.choice(_next)}: {res['response']['text']}"
            else:
                res['response'][
                    'text'] = f"{random.choice(wrong)} Правильный ответ: {sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer']}. \n{random.choice(_next)}: {res['response']['text']}"

        sessionStorage[user_id]['id'] += 1

    if sessionStorage[user_id]['mode'] == 'картины':
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
            if sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1].lower() \
                    in req['request']['original_utterance'].lower():
                res['response']['card']['title'] = random.choice(right)
            else:
                res['response']['card']['title'] \
                    = f"{random.choice(wrong)} Правильный ответ: {sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic'] - 1]}."

            if sessionStorage[user_id]['idPic'] == len(sessionStorage[user_id]['arrayPic']):
                random.shuffle(sessionStorage[user_id]['arrayPic'])
                sessionStorage[user_id]['idPic'] = 0
            res['response']['card']['image_id'] = \
                portraits.get(sessionStorage[user_id]['arrayPic'][sessionStorage[user_id]['idPic']])
            res['response']['card']['title'] += ' Кто изображен на фотографии?'
        res['response']['text'] = ''
        sessionStorage[user_id]['idPic'] += 1

    if sessionStorage[user_id]['mode'] == 'термины':
        pass

    # если в нашем запросе 'закрыть' заканчиваем сессию
    if 'закрыть' in req['request']['original_utterance'].lower():
        res['response']['text'] = 'Пока!'
        res['response']['end_session'] = True
        return
    res['response']['buttons'] = [
        {'title': suggest, 'hide': True}
        for suggest in sessionStorage[user_id]['suggests'][2:]
    ]


if __name__ == '__main__':
    app.run()
