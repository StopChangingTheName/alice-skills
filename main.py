from flask import Flask, request
import logging
import json
from flask_ngrok import run_with_ngrok
import os

# не удаляйте этот путь т.к. у меня проблема с открытием data.json
with open('C:/Users/Daniel/dev/github/alice-skills/Data.json', encoding='utf8') as f:
    # альтернатива для вас:
    # with open('Data.json', encoding='utf8') as f:
    data = json.loads(f.read())['test']

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
        sessionStorage[user_id] = {
            'suggests': [
                "Случайные даты",
            ]
        }

        res['response']['text'] = 'Привет! Выбери режим:'

        res['response']['buttons'] = [
            {'title': suggest, 'hide': True}
            for suggest in sessionStorage[user_id]['suggests']
        ]
        return

    if req['request']['original_utterance'].lower() == "Привет":
        res['response']['text'] = 'Правильно!'
        res['response']['end_session'] = True
        return

    res['response']['text'] = 'Дата из json'
    res['response']['buttons'] = [
        {'title': suggest, 'hide': True}
        for suggest in sessionStorage[user_id]['suggests']
    ]


if __name__ == '__main__':
    app.run()
