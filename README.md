**Установка и запуск**

Клонируйте репозиторий:
```
git clone
cd api_yamdb
```
Создайте и активируйте виртуальное окружение:
```
python -m venv venv
source venv/bin/activate  # для macOS
```

Установите зависимости:
```
pip install -r requirements.txt
```
Примените миграции:
```
python manage.py migrate
```

Запустите сервер:
```
python manage.py runserver
```

### Полная документация доступна по адресу:
http://127.0.0.1:8000/redoc/
