from fastapi.testclient import TestClient
from main import app
import random
import string

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200

def test_get_users():
    # Сначала аутентифицируемся и получим токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для запроса к маршруту /users/
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Проверяем, что пользователь 'testuser' существует в списке пользователей
    assert any(user["username"] == "testuser" for user in data)

def test_create_user():
    # Генерируем уникальное имя пользователя и email
    unique_username = ''.join(random.choices(string.ascii_lowercase, k=8))
    unique_email = f"{unique_username}@example.com"

    # Сначала аутентифицируемся и получим токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для создания нового пользователя
    response = client.post(
        "/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == unique_username
    assert data["email"] == unique_email

    # Проверяем, что повторная регистрация с тем же username или email возвращает ошибку
    response = client.post(
        "/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_authentication():
    # Проверяем успешную аутентификацию
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Проверяем, что неправильный username или password возвращает ошибку
    login_response = client.post(
        "/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert login_response.status_code == 401

    # Проверяем, что истёкший или неправильный токен вызывает ошибку авторизации
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_get_current_user():
    # Сначала аутентифицируемся и получим токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для получения информации о текущем пользователе
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_update_user():
    # Сначала аутентифицируемся и получим токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Генерируем уникальное имя пользователя и email
    unique_username = ''.join(random.choices(string.ascii_lowercase, k=8))
    unique_email = f"{unique_username}@example.com"

    # Создаем нового пользователя
    response = client.post(
        "/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Обновляем данные пользователя
    updated_email = f"{unique_username}_updated@example.com"
    response = client.put(
        f"/users/{user_id}",
        json={"full_name": "Updated User", "email": updated_email},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"
    assert data["email"] == updated_email

    # Проверяем, что обновление с некорректными данными возвращает ошибку
    response = client.put(
        f"/users/{user_id}",
        json={"email": "invalid_email"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

    # Проверяем, что невозможно изменить данные без правильного токена
    response = client.put(
        f"/users/{user_id}",
        json={"full_name": "Updated User"},
        headers={"Authorization": f"Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_delete_user():
    # Сначала аутентифицируемся и получим токен
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Генерируем уникальное имя пользователя и email
    unique_username = ''.join(random.choices(string.ascii_lowercase, k=8))
    unique_email = f"{unique_username}@example.com"

    # Создаем нового пользователя
    response = client.post(
        "/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    user_id = response.json()["id"]

    # Удаляем пользователя
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    # Проверяем, что повторная попытка удалить того же пользователя возвращает ошибку
    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
