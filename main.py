from flask import Flask, request
import logging
from flask_ngrok import run_with_ngrok
import json
import random
import copy

# не удаляйте этот путь т.к. у меня проблема с открытием data.json
with open('C:/Users/Daniel/dev/github/alice-skills/Data.json', encoding='utf8') as f:
    # альтернатива для вас:
    # with open('Data.json', encoding='utf8') as f:
    data = json.loads(f.read())['test']  # массив из словарей

app = Flask(__name__)
run_with_ngrok(app)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']
    # если 1 раз
    if req['session']['new']:
        arr = copy.deepcopy(data)
        random.shuffle(arr)  # перемешанная data
        sessionStorage[user_id] = {
            'suggests': [
                "Случайные даты",
                "Закрыть"
            ],
            'test': arr,
            'id': 0
        }
        res['response']['text'] = 'Привет! Выбери режим:'

        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        return

    # если в нашем запросе 'закрыть' заканчиваем сессию
    if req['request']['original_utterance'].lower() in ['закрыть', 'стоп']:
        res['response']['text'] = 'Пока!'
        res['response']['end_session'] = True
        return

    res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
    print('Вопрос: ', sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question'])
    print('Ответ: ', sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['answer'])
    print('Введенное мною: ', req['request']['original_utterance'].lower())
    if req['request']['original_utterance'].lower() == sessionStorage[user_id]['test'][sessionStorage[user_id]['id']][
        'answer']:
        res['response']['text'] = 'Верно!'

    res['response']['buttons'] = [
        {'title': suggest, 'hide': True}
        for suggest in sessionStorage[user_id]['suggests']
    ]
    sessionStorage[user_id]['id'] += 1


if __name__ == '__main__':
    app.run()
