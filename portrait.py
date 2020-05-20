
portraits = {
    'Петр Первый': '1521359/10784a607c8badd66f5d',
    'Королев': '997614/34c94ee0045f88da4069',
    'Ленин': '213044/6688e801118b5c50e322',
    'Павел Первый': '1030494/b7339d700c0cb5e7baf8'
    # 'Александр 3': '1652229/3653b9133fb66896f180',
    # 'Анна Иоанновна': '213044/23e9a3ca841ffebc31af',
    # 'Вещий Олег': '965417/bc1505dffd077e5985c6',
    # 'Жуков': '213044/92444f68b5e441beaf35',
    # 'Калашников': '1030494/a2cd9c5f7ef1cda11c4c',
    # 'Кеннеди': '1652229/7257b3f0ed312778be4d',
    # 'Наполеон 3': '213044/b70f59b59f705cd61aa8',
    # 'Невский': '1656841/e1ae9cbae3905a526e74',
    # 'Путин': '965417/3c59d7ebc7fc40ea6bbd',
    # 'Сахаров': '1030494/918ce1b846eb99e17bda',
    # 'Хрущев': '213044/d374d42cf13155100dc6',
    # 'Циолковский': '965417/5ccdc71dbe8b3675758b',
    # 'Эйнштейн': '213044/0942ff5f0acc3ab8f83f'
}


def get_last_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('last_name', None)
