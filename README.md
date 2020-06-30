# Знатоки истории
## Навык для Яндекс Алисы на Python
# Ссылка на навык в [каталоге](https://dialogs.yandex.ru/store/skills/1424e7f5-ege-po-istorii)
### Как запустить локально:
1. Установите необходимые модули
2. Раскоментируйте следующие строки:
```python
# эти строки нужны для запуска программы через ngrok
from flask_ngrok import run_with_ngrok
run_with_ngrok(app)
```
```python
# keep_alive() - эту строку комментируем (она для продакшена)
app.run() # эту раскомментируем (она для запуска в режиме тестирования)
```
3. Вставьте в поле Webhook URL в [Диалогах](https://dialogs.yandex.ru/developer) ссылку, который сгенерировал ngrok, с /post на конце.
  Пример: https://a9f03915.ngrok.io/post
4. Тестируйте :)
  ![Imgur](https://i.imgur.com/txwTYJr.png)
