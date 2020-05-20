
portraits = {
    'Петр Первый': '1521359/10784a607c8badd66f5d',
    'Королев': '997614/34c94ee0045f88da4069',
    'Ленин': '213044/6688e801118b5c50e322',
    'Павел 1': '1030494/b7339d700c0cb5e7baf8'
}


def get_last_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('last_name', None)
