import allure
import pytest
from conftest import BASE_URL, extract_item_id

class TestDeleteV2:
    # ТК-29
    @allure.title("ТК-29: Успешное удаление существующего объявления")
    @allure.description("Проверяет, что DELETE /api/2/item/:id удаляет объект и он становится недоступен")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Позитивный сценарий")
    def test_delete_existing(self, api_client, valid_payload):
        with allure.step("Создание тестового объявления"):
            create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
            assert create_resp.status_code == 200
            item_id = extract_item_id(create_resp.json())

        with allure.step(f"Удаление объявления через DELETE /api/2/item/{item_id}"):
            del_resp = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
            assert del_resp.status_code == 200

        with allure.step("Проверка, что объявление больше не доступно"):
            get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
            assert get_resp.status_code == 404

    # ТК-31
    def test_delete_nonexistent(self, api_client):
        resp = api_client.delete(f"{BASE_URL}/api/2/item/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    # ТК-32
    def test_delete_invalid_format(self, api_client):
        resp = api_client.delete(f"{BASE_URL}/api/2/item/not-a-uuid")
        assert resp.status_code in [400, 404]

    # ТК-33
    @allure.title("ТК-33: Повторное удаление уже удаленного объявления")
    @allure.description("Проверяет идемпотентность удаления: второй запрос должен вернуть 404")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Корнер-кейс")
    def test_delete_twice(self, api_client, valid_payload):
        with allure.step("Создание и первое удаление объявления"):
            create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
            item_id = extract_item_id(create_resp.json())
            api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")

        with allure.step("Повторная попытка удаления того же ID"):
            resp = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        
        with allure.step("Проверка статуса 404 (объект уже удалён)"):
            assert resp.status_code == 404