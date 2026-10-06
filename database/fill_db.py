import os
import random
import argparse
from datetime import date, timedelta
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Загружаем переменные окружения (DATABASE_URL)
load_dotenv()

# Обязательное требование: фиксированный seed для воспроизводимости БД при каждом запуске
random.seed(42)

VOLUMES = {
    'small': {'readers': 50, 'books': 100, 'copies': 200, 'checkouts': 300},
    'working': {'readers': 3000, 'books': 10000, 'copies': 30000, 'checkouts': 50000}
}

def fill_database(size):
    params = VOLUMES[size]
    
    # Подключение к БД (строка берется из .env)
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    print(f"Очистка таблиц перед наполнением...")
    cur.execute("""
        TRUNCATE TABLE oleg_gusev.checkouts, oleg_gusev.copies, 
        oleg_gusev.books, oleg_gusev.readers RESTART IDENTITY CASCADE;
    """)
    
    print(f"Генерация данных ({size} объем)...")
    
    # 1. Читатели
    readers = [(f"Читатель {i}",) for i in range(1, params['readers'] + 1)]
    execute_values(cur, "INSERT INTO oleg_gusev.readers (full_name) VALUES %s", readers)
    
    # 2. Книги
    books = [(f"Книга {i}", f"Автор {i % 100 + 1}") for i in range(1, params['books'] + 1)]
    execute_values(cur, "INSERT INTO oleg_gusev.books (title, author) VALUES %s", books)
    
    # 3. Экземпляры
    copies = [(random.randint(1, params['books']), 'свободен') for _ in range(params['copies'])]
    execute_values(cur, "INSERT INTO oleg_gusev.copies (book_id, status) VALUES %s", copies)
    
    # 4. Выдачи
    checkouts = []
    base_date = date(2025, 1, 1)
    
    for _ in range(params['checkouts']):
        copy_id = random.randint(1, params['copies'])
        reader_id = random.randint(1, params['readers'])
        issue_date = base_date + timedelta(days=random.randint(0, 365))
        due_date = issue_date + timedelta(days=14) # Выдаем на две недели
        
        # 20% шанс, что книгу еще не вернули (return_date = None)
        # Иначе книга возвращена со случайной задержкой (потенциальная просрочка)
        is_returned = random.random() > 0.2
        return_date = issue_date + timedelta(days=random.randint(5, 30)) if is_returned else None
        
        checkouts.append((copy_id, reader_id, issue_date, due_date, return_date))
        
    execute_values(cur, """
        INSERT INTO oleg_gusev.checkouts (copy_id, reader_id, issue_date, due_date, return_date) 
        VALUES %s
    """, checkouts)
    
    # Обновляем статусы экземпляров, которые сейчас на руках
    cur.execute("""
        UPDATE oleg_gusev.copies 
        SET status = 'выдан' 
        WHERE id IN (SELECT copy_id FROM oleg_gusev.checkouts WHERE return_date IS NULL);
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Наполнение завершено!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', choices=['small', 'working'], required=True)
    args = parser.parse_args()
    fill_database(args.size)