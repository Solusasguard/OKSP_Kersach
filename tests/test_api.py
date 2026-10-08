from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_get_books_pagination():
    response = client.get("/api/books?page=1&size=5")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) <= 5

def test_checkout_already_issued_copy():
    # Первая выдача проходит
    client.post("/api/checkouts?copy_id=1&reader_id=2")
    
    # Вторая выдача того же экземпляра должна быть заблокирована
    response_duplicate = client.post("/api/checkouts?copy_id=1&reader_id=3")
    assert response_duplicate.status_code == 403
    assert response_duplicate.json()["detail"] == "Экземпляр уже выдан"