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
                "Картины",
                "Термины",
                "Закрыть",
                "В меню",
            ],
            'test': arr,
            'id': 0,
            'lastQ': False,
            'mode': ''
        }
        res['response']['text'] = 'Привет! Выбери режим:'

        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        return
    # ставим режим
    if req['request']['original_utterance'].lower() == 'случайные даты':
        sessionStorage[user_id]['mode'] = 'случайные даты'
    if req['request']['original_utterance'].lower() == 'картины':
        sessionStorage[user_id]['mode'] = 'картины'
    if req['request']['original_utterance'].lower() == 'термины':
        sessionStorage[user_id]['mode'] = 'термины'

    if sessionStorage[user_id]['mode'] == 'случайные даты':
        if not sessionStorage[user_id]['lastQ']:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['question']
            sessionStorage[user_id]['lastQ'] = True
        else:
            res['response']['text'] = sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question']
            print(sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['question'])
            print(sessionStorage[user_id]['test'][sessionStorage[user_id]['id']]['answer'])
            print('моё ', req['request']['original_utterance'].lower())
            if req['request']['original_utterance'].lower() == \
                    sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1][
                        'answer']:
                res['response']['text'] = f"Верно! Следующий вопрос: {res['response']['text']}"
            else:
                res['response'][
                    'text'] = f"Неверно, правильный ответ: {sessionStorage[user_id]['test'][sessionStorage[user_id]['id'] - 1]['answer']} .Следующий вопрос: {res['response']['text']}"

        sessionStorage[user_id]['id'] += 1

    if sessionStorage[user_id]['mode'] == 'картины':
        pass
    if sessionStorage[user_id]['mode'] == 'термины':
        pass

    # если в нашем запросе 'закрыть' заканчиваем сессию
    if req['request']['original_utterance'].lower() in ['закрыть', 'стоп']:
        res['response']['text'] = 'Пока!'
        res['response']['end_session'] = True
        return


if __name__ == '__main__':
    app.run()
