from werkzeug.security import generate_password_hash, check_password_hash

portraits = {
    'Петр 1': '965417/24d6b2e32bbbd4bbc005',
    'Ленин': '213044/830f4c53cf86a3202b93',
    'Павел 1': '213044/c6e5a017fde373a00c51',
    'Александр 3': '213044/3fd5b0758533fc1be811',
    'Анна Иоанновна': '213044/8f8d815cda309ba80d84',
    'Вещий Олег': '1652229/44fb71b3ee314c070458',
    'Жуков': '213044/dd31cd5b27f6725fac74',
    'Калашников': '965417/7f9b58dbb03f58a8cd4c',
    'Кеннеди': '213044/187e5f5dc6ada4b3a4ec',
    'Наполеон 3': '1652229/1dc87be5de29fdee93ca',
    'Невский': '1652229/c5239457dbeffce67377',
    'Путин': '213044/8e6a3d2c1299a268c3dd',
    'Сахаров': '1030494/29acc53e86194620c956',
    'Хрущев': '1030494/1e370abd1dfd7cb7a88a',
    'Циолковский': '213044/d57f507790d4cdd3e382',
    'Эйнштейн': '1652229/2650898d0f5169cdb11f',
    'Маяковский': '1030494/115bafcdd625e023aeae',
    'Уваров': '1030494/c3658228ec792c77eb3a',
    'Чапаев': '1652229/f4cda5e349776185fb2c'
}


def get_last_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('last_name', None)


def hash_pass(pswd):
    return generate_password_hash(pswd)


def unhash_pass(hash, user_id):
    return check_password_hash(hash, user_id)
