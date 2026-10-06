import requests
import time
import statistics

BASE_URL = "http://localhost:8000"
# Тестируем все три эндпоинта из контракта
ENDPOINTS = [
    ("GET", "/api/books?page=1&size=20"),
    ("GET", "/api/summary"),
    # Для POST берем случайные ID. Даже если вернется 403, база данных
    # все равно выполнит тяжелые запросы проверок, что нам и нужно измерить.
    ("POST", "/api/checkouts?copy_id=50&reader_id=10")
]

def measure(method, path, warmup=5, runs=25):
    url = BASE_URL + path
    
    # 1. Прогрев (результаты не учитываем)
    for _ in range(warmup):
        requests.request(method, url)
        
    # 2. Серия замеров
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        requests.request(method, url)
        end = time.perf_counter()
        times.append((end - start) * 1000) # переводим в миллисекунды
        
    # 3. Расчет метрик
    times.sort()
    median = statistics.median(times)
    # Индекс для 95-го процентиля
    p95_idx = int(len(times) * 0.95) - 1 
    p95 = times[p95_idx]
    max_time = max(times)
    
    print(f"{method} {path}")
    print(f"Медиана: {median:.2f} мс | 95-й процентиль: {p95:.2f} мс | Макс: {max_time:.2f} мс\n")

if __name__ == "__main__":
    print("=== Замеры производительности ===")
    for method, path in ENDPOINTS:
        measure(method, path)

        