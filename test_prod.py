import requests
import random
import string

# Base URL for the API in production
BASE_URL = "http://localhost:8000"

def test_read_main():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200

def test_get_users():
    # Сначала аутентифицируемся и получим токен
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для запроса к маршруту /users/
    response = requests.get(
        f"{BASE_URL}/users/",
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
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для создания нового пользователя
    response = requests.post(
        f"{BASE_URL}/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == unique_username
    assert data["email"] == unique_email

    # Проверяем, что повторная регистрация с тем же username или email возвращает ошибку
    response = requests.post(
        f"{BASE_URL}/register/",
        json={"username": unique_username, "email": unique_email, "full_name": "New User", "password": "password123"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400

def test_authentication():
    # Проверяем успешную аутентификацию
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Проверяем, что неправильный username или password возвращает ошибку
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "wronguser", "password": "wrongpassword"}
    )
    assert login_response.status_code == 401

    # Проверяем, что истёкший или неправильный токен вызывает ошибку авторизации
    response = requests.get(
        f"{BASE_URL}/users/",
        headers={"Authorization": f"Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_get_current_user():
    # Сначала аутентифицируемся и получим токен
    login_response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "testuser", "password": "password123"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Используем токен для получения информации о текущем пользователе
    response = requests.get(
        f"{BASE_URL}/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

if __name__ == "__main__":
    test_read_main()
    test_authentication()
    test_get_users()
    test_create_user()
    test_get_current_user()
    print("All production tests passed!") 