# Сервис библиотеки
Выдает экземпляры книг читателям, контролирует возвраты и автоматически рассчитывает просрочку и штрафы. Учебный сервис курсовой работы по дисциплине «Оптимизация клиент-серверных приложений».

## Требования
* PostgreSQL 16
* Python 3.12 (или выше)

## Установка и запуск
```bash
git clone https://github.com/Solusasguard/OKSP_Kersach.git
cd OKSP_Kersach
cp .env.example .env
# Обязательно укажи в .env свой реальный пароль от БД и убедись, что используется IP 127.0.0.1 (а не localhost) перед следующими шагами!

pip install -r requirements.txt
psql -U postgres -d oleg_gusev -f database/schema.sql
python database/fill_db.py --size small
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

## Переменные окружения
| Переменная | Назначение | Пример |
|---|---|---|
| DATABASE_URL | подключение к БД | postgresql://postgres:changeme@127.0.0.1:5432/oleg_gusev |
| APP_PORT | порт сервиса | 8000 |

## Проверка работоспособности
Интерфейс API открывается по адресу http://localhost:8000/docs.

## Тесты
```bash
pytest tests/
```

## Программный интерфейс
| Метод и путь | Параметры | Ответ | Ошибки |
|---|---|---|---|
| GET /api/books | page, size | {"items": [...], "total": N} | 401 |
| POST /api/checkouts | copy_id, reader_id | 201 и запись о выдаче | 401, 403, 404 |
| GET /api/summary | - | Сводка: выдано на руки, просрочено, популярные книги | 401 |
