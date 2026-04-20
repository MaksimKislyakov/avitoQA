import re
import random
import pytest
import requests

BASE_URL = "https://qa-internship.avito.com"

@pytest.fixture(scope="session")
def api_client():
    """Сессия с переиспользуемым соединением"""
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session

@pytest.fixture
def unique_seller_id():
    """Генерирует уникальный sellerID в диапазоне 111111–999999"""
    return random.randint(111111, 999999)

@pytest.fixture
def valid_payload(unique_seller_id):
    """Мокированное тело запроса с валидными данными"""
    return {
        "sellerID": unique_seller_id,
        "name": f"Тестовый товар {random.randint(1, 100000)}",
        "price": random.randint(100, 100000),
        "statistics": {"likes": 1, "viewCount": 10, "contacts": 1}
    }

def extract_item_id(response_json):
    """Извлекает ID из ответа (работает с документированным и фактическим форматом)"""
    if "id" in response_json:
        return response_json["id"]
    if "status" in response_json:
        # (BUG-1)
        match = re.search(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})", response_json["status"])
        if match:
            return match.group(1)
    return None

@pytest.fixture
def created_item(api_client, valid_payload):
    """Создает объявление и возвращает его ID + payload для других тестов"""
    resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
    item_id = extract_item_id(resp.json())
    if not item_id:
        pytest.fail(f"Не удалось извлечь ID из POST ответа: {resp.text}")
    yield {"id": item_id, "payload": valid_payload}
    api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")