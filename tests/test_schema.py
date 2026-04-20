import re
import allure
import pytest
from conftest import BASE_URL, extract_item_id

class TestSchemaValidation:
    # ТК-36
    @allure.title("ТК-36: Проверка формата поля id в ответе")
    @allure.description("Проверяет, что ID возвращается в формате UUID (строка)")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Schema validation")
    def test_id_format(self, api_client, valid_payload):
        with allure.step("Создание объявления для проверки формата ID"):
            create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
            item_id = extract_item_id(create_resp.json())
        
        with allure.step("Валидация формата UUID"):
            assert item_id is not None
            assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", item_id)
            allure.attach(f"Валидный UUID: {item_id}", name="Valid UUID", attachment_type=allure.attachment_type.TEXT)
    # ТК-37
    @allure.title("ТК-37: Проверка формата поля createdAt")
    @allure.description("Проверяет, что дата возвращается в формате ISO 8601")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.issue(name="BUG-9: Некорректный формат даты", url="file:///D:/Codes/avitoQA/BUGS.md#bug-9")
    @allure.story("Schema validation")
    def test_created_at_format(self, api_client, created_item):
        item_id = created_item["id"]
        
        with allure.step("Получение объявления для проверки createdAt"):
            get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
            created_at = get_resp.json()[0].get("createdAt", "")
        
        with allure.step("Валидация формата даты"):
            assert isinstance(created_at, str)
            if "T" not in created_at or created_at.count("+0300") != 1:
                allure.attach(f"Некорректный формат: {created_at}", name="Invalid Date Format", attachment_type=allure.attachment_type.TEXT)
                pytest.xfail("BUG-9: Неверный формат даты (ожидается ISO 8601)")

    # ТК-38
    def test_response_fields(self, api_client, created_item):
        item_id = created_item["id"]
        get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        data = get_resp.json()[0]
        expected_fields = {"id", "sellerId", "name", "price", "statistics", "createdAt"}
        assert set(data.keys()) == expected_fields, f"Лишние или недостающие поля: {set(data.keys())}"