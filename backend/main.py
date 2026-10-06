import os
import time
from datetime import date, timedelta
from fastapi import FastAPI, Query, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="Library Service API", version="0.1.0")

def get_db_connection():
    # Подключение к БД, возвращаем строки в виде словарей (dict)
    return psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)


@app.get("/api/books")
def get_books(page: int = Query(1, ge=1), size: int = Query(20, ge=1, le=100)):
    """Получение списка книг с постраничным выводом"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        offset = (page - 1) * size
        
        cur.execute("""
            SELECT id, title, author 
            FROM oleg_gusev.books 
            ORDER BY id 
            LIMIT %s OFFSET %s
        """, (size, offset))
        books = cur.fetchall()
        
        cur.execute("SELECT COUNT(*) as total FROM oleg_gusev.books")
        total = cur.fetchone()['total']
        
        return {"items": books, "total": total}
    finally:
        cur.close()
        conn.close()


@app.post("/api/checkouts", status_code=201)
def create_checkout(copy_id: int, reader_id: int):
    """Выдача экземпляра читателю с проверкой долгов"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # 1. Проверяем статус экземпляра
        cur.execute("SELECT status FROM oleg_gusev.copies WHERE id = %s", (copy_id,))
        copy = cur.fetchone()
        if not copy:
            raise HTTPException(status_code=404, detail="Экземпляр не найден")
        if copy['status'] != 'свободен':
            raise HTTPException(status_code=403, detail="Экземпляр уже выдан")

        # 2. Проверяем долги читателя
        cur.execute("""
            SELECT COUNT(*) as debts 
            FROM oleg_gusev.checkouts 
            WHERE reader_id = %s AND return_date IS NULL AND due_date < CURRENT_DATE
        """, (reader_id,))
        debts = cur.fetchone()['debts']
        if debts > 0:
            raise HTTPException(status_code=403, detail="У читателя есть просроченные книги")

        # 3. Выдача книги
        issue_date = date.today()
        due_date = issue_date + timedelta(days=14)
        
        cur.execute("""
            INSERT INTO oleg_gusev.checkouts (copy_id, reader_id, issue_date, due_date)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (copy_id, reader_id, issue_date, due_date))
        checkout_id = cur.fetchone()['id']
        
        # 4. Обновление статуса экземпляра
        cur.execute("UPDATE oleg_gusev.copies SET status = 'выдан' WHERE id = %s", (copy_id,))
        
        conn.commit()
        return {"id": checkout_id, "message": "Книга успешно выдана"}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


@app.get("/api/summary")
def get_summary():
    """Сводка по библиотеке: на руках, просрочено, популярные книги"""
    start_total = time.perf_counter()
    
    # Запускаем таймер БД строго ДО подключения
    start_db = time.perf_counter() 
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Экземпляры на руках
        cur.execute("SELECT COUNT(*) as count FROM oleg_gusev.checkouts WHERE return_date IS NULL")
        on_hand = cur.fetchone()['count']
        
        # Просроченные экземпляры (восстановленный блок)
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM oleg_gusev.checkouts 
            WHERE return_date IS NULL AND due_date < CURRENT_DATE
        """)
        overdue = cur.fetchone()['count']
        
        # Топ-5 популярных книг
        cur.execute("""
            SELECT b.title, COUNT(c.id) as checkout_count 
            FROM oleg_gusev.books b
            JOIN oleg_gusev.copies cp ON b.id = cp.book_id
            JOIN oleg_gusev.checkouts c ON cp.id = c.copy_id
            GROUP BY b.id, b.title
            ORDER BY checkout_count DESC
            LIMIT 5
        """)
        popular_books = cur.fetchall()
        
        end_db = time.perf_counter()
        
        # Расчет времени
        db_time = (end_db - start_db) * 1000
        total_time = (time.perf_counter() - start_total) * 1000
        app_time = total_time - db_time
        
        # Вывод в консоль сервера для скриншота
        print("\n=== ПРОФИЛИРОВАНИЕ GET /api/summary ===")
        print(f"Общее время выполнения:  {total_time:.2f} мс")
        print(f"Время в PostgreSQL (БД): {db_time:.2f} мс")
        print(f"Время в коде FastAPI:    {app_time:.2f} мс")
        print("=========================================\n")
        
        return {
            "copies_on_hand": on_hand,
            "copies_overdue": overdue,
            "popular_books": popular_books
        }
    finally:
        cur.close()
        conn.close()