# Сервис-справочник организаций

## Описание
1. API сервис, представляющий собой редактируемый справочник организаций, их контактов и видов деятельности
2. В приложении реализован полный CRUD для зданий, располагающихся в них организаций, а также видов деятельности организаций
3. В списке организаций настроена фильтрация по названию организации, зданию, виду деятельности, а также по названию деятельности вниз по дереву
4. В списках зданий и организаций также настроен поиск относительно заданной точки в указанном радиусе

## Установка проекта
1. Клонирование проекта из [GitHub](https://github.com/yolarus/organizations-directory) по HTTPS-токену или SSH-ключу.
2. Создание и заполнение файла .env своими данными. В качестве статического токена можно взять любой, например, eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYzMjkyODM2LCJ1c2VyX3V1aWQiOiI0NWQ4OWUzMi0zOWZjLTQ2NDMtOTQwMS05NDhlNWZhZTBhOWQiLCJyZW1lbWJlcl9tZSI6ZmFsc2V9.svinO16t1PwFwsqvEVLkGYXbL5oL-ftwwMhKhbSt2Vg

## Запуск через docker
1. `docker compose up -d --build`
2. При желании можно наполнить БД тестовыми данными из файла organizations
   - `docker exec -it organizations_db bash`
   - `pg_restore -U postgres -d organizations data/organizations`

## Запуск напрямую
1. Создание виртуального окружения `python3 -m venv venv`
2. Активация виртуального окружения `source venv/bin/activate`
3. Установка зависимостей `pip install -r requirements.txt`
4. Запуск приложения `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
5. Применение миграций `alembic upgrade head`
6. При желании можно наполнить БД тестовыми данными из файла organizations
   - `pg_restore -U username -d database_name organizations`

## Тестирование
1. Тесты покрывают 90 % кода. Запуск `pytest`

## Документация
Документация доступа по ссылкам:
* http://localhost/api/redoc/
* http://localhost/api/swagger/
