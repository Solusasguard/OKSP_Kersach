# Сервис библиотеки
Выдает экземпляры книг читателям, контролирует возвраты и автоматически рассчитывает просрочку и штрафы. Учебный сервис курсовой работы по дисциплине «Оптимизация клиент-серверных приложений».

## Требования
* PostgreSQL 16
* Python 3.12 (или выше)

## Установка и запуск

```bash
git clone https://github.com/Solusasguard/OKSP_Kersach.git
cd library-service
cp .env.example .env
# Обязательно укажите в .env свой реальный пароль от БД перед следующими шагами!

pip install -r requirements.txt
psql -U postgres -d oleg_gusev -f database/schema.sql
python database/fill_db.py --size small
uvicorn backend.main:app --host 0.0.0.0 --port 8080