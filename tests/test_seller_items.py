import allure
import pytest
from conftest import BASE_URL

class TestSellerItems:
    # ТК-16
    @allure.title("ТК-16: Получение списка объявлений продавца (несколько товаров)")
    @allure.description("Проверяет, что эндпоинт возвращает все объявления конкретного продавца")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Позитивный сценарий")
    def test_get_seller_items(self, api_client, valid_payload):
        sid = valid_payload["sellerID"]
        
        with allure.step("Создание двух объявлений для одного продавца"):
            for i in range(2):
                payload = {**valid_payload, "name": f"Товар #{i}"}
                resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload, headers={"Content-Type": "application/json"})
                assert resp.status_code == 200

        with allure.step(f"Запрос списка объявлений для sellerID={sid}"):
            resp = api_client.get(f"{BASE_URL}/api/1/{sid}/item")
        
        with allure.step("Проверка, что в ответе минимум 2 объявления"):
            assert resp.status_code == 200
            assert isinstance(resp.json(), list) and len(resp.json()) >= 2

    # ТК-17
    def test_get_empty_seller(self, api_client, unique_seller_id):
        resp = api_client.get(f"{BASE_URL}/api/1/{unique_seller_id}/item")
        assert resp.status_code == 200
        assert resp.json() == []

    # ТК-18
    @allure.title("ТК-18: Некорректный тип sellerID в URL")
    @allure.description("Проверяет валидацию параметра sellerID в пути запроса")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Негативный сценарий")
    def test_get_negative_seller_id(self, api_client):
        with allure.step("Отправка GET запроса с отрицательным sellerID: -1"):
            resp = api_client.get(f"{BASE_URL}/api/1/-1/item")
        
        if resp.status_code == 200:
            allure.attach("Сервер принял отрицательный sellerID в URL", name="Bug Confirmation", attachment_type=allure.attachment_type.TEXT)
            pytest.xfail("BUG-10: Сервер принял отрицательный sellerID в URL")
        
        assert resp.status_code == 400

    # ТК-19
    def test_get_invalid_seller_id_format(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/abc-def/item")
        assert resp.status_code in [400, 404]