import allure
import pytest
from conftest import BASE_URL

class TestGetItem:
    # ТК-12
    @allure.epic("Микросервис объявлений Avito")
    @allure.feature("Получение объявлений")
    @allure.title("ТК-12: Успешное получение существующего объявления")
    @allure.description("Проверяет, что созданный объект можно получить по его ID через GET /api/1/item/:id")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Позитивный сценарий")
    def test_get_existing(self, api_client, created_item):
        item_id = created_item["id"]
        
        with allure.step(f"Отправка GET запроса на /api/1/item/{item_id}"):
            resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        
        with allure.step("Проверка статуса 200 OK и наличия данных"):
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list) and len(data) > 0
            assert data[0]["id"] == item_id
        
        # BUG-9
        created_at = data[0].get("createdAt", "")
        if "T" not in created_at:
            allure.attach(f"Некорректный формат даты: {created_at}", name="Date Format Issue", attachment_type=allure.attachment_type.TEXT)
            pytest.xfail("BUG-9: createdAt не в формате ISO 8601")

    # ТК-13
    @allure.title("ТК-13: Запрос с несуществующим ID")
    @allure.description("Проверяет, что сервер корректно возвращает 404 для несуществующего объявления")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Негативный сценарий")
    def test_get_nonexistent(self, api_client):
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        with allure.step(f"Отправка GET запроса с несуществующим ID: {fake_id}"):
            resp = api_client.get(f"{BASE_URL}/api/1/item/{fake_id}")
        
        with allure.step("Проверка статуса 404 Not Found"):
            assert resp.status_code == 404
            assert "result" in resp.json()

    # ТК-14
    def test_get_invalid_format(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/item/!@#$%^")
        assert resp.status_code == 400

    # ТК-15
    def test_get_idempotent(self, api_client, created_item):
        item_id = created_item["id"]
        responses = [api_client.get(f"{BASE_URL}/api/1/item/{item_id}") for _ in range(5)]
        assert all(r.status_code == 200 for r in responses)
        assert all(r.json() == responses[0].json() for r in responses)