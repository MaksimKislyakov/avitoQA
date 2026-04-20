import time

import allure
import pytest

from conftest import BASE_URL, extract_item_id, log_api_request, log_api_response


class TestCreateItem:
    # ТК-1
    @allure.title("ТК-1: Успешное создание объявления со всеми валидными полями")
    @allure.description(
        "Проверяет корректность работы POST /api/1/item при передаче всех обязательных полей. Ожидается статус 200 и возврат уникального ID."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Позитивный сценарий")
    def test_create_valid(self, api_client, valid_payload):
        with allure.step("Формирование и отправка POST запроса"):
            log_api_request("POST", f"{BASE_URL}/api/1/item", payload=valid_payload)
            resp = api_client.post(
                f"{BASE_URL}/api/1/item",
                json=valid_payload,
                headers={"Content-Type": "application/json"},
            )
            log_api_response(resp)

        with allure.step("Проверка статуса ответа 200 OK"):
            assert resp.status_code == 200

        with allure.step("Валидация структуры ответа и извлечение ID"):
            item_id = extract_item_id(resp.json())
            assert item_id is not None, "ID не найден в ответе"
            allure.attach(
                f"Сгенерированный ID: {item_id}",
                name="Created Item ID",
                attachment_type=allure.attachment_type.TEXT,
            )

    # ТК-2
    @allure.title("ТК-2: Создание объявления с нулевой ценой")
    @allure.description(
        "Проверяет валидацию поля price. Ожидается отказ в создании (400) или фиксация бага BUG-2."
    )
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_price_zero(self, api_client, valid_payload):
        payload = {**valid_payload, "price": 0}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        if resp.status_code == 400:
            pytest.xfail("BUG-2: price=0 возвращает 400 вместо 200")
        assert resp.status_code == 200

    # ТК-3
    def test_create_stats_zero(self, api_client, valid_payload):
        payload = {**valid_payload, "statistics": {"likes": 0, "viewCount": 0, "contacts": 0}}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        if resp.status_code == 400:
            pytest.xfail("BUG-3: stats=0 возвращает 400 вместо 200")
        assert resp.status_code == 200

    # ТК-4
    def test_create_missing_field(self, api_client, valid_payload):
        payload = {**valid_payload}
        del payload["price"]
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        assert resp.status_code == 400
        assert "обязательно" in resp.json().get("result", {}).get("message", "").lower()

    # ТК-5
    def test_create_wrong_type(self, api_client, valid_payload):
        payload = {**valid_payload, "price": "15000"}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        # BUG-4
        assert resp.status_code == 400

    # ТК-6
    @allure.title("ТК-6: Создание объявления с отрицательной ценой")
    @allure.description(
        "Проверяет валидацию поля price. Ожидается отказ в создании (400) или фиксация бага BUG-5."
    )
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_negative_price(self, api_client, valid_payload):
        payload = {**valid_payload, "price": -100}

        with allure.step("Отправка запроса с price=-100"):
            log_api_request("POST", f"{BASE_URL}/api/1/item", payload=payload)
            resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
            log_api_response(resp)

        if resp.status_code == 200:
            allure.attach(
                "Сервер принял отрицательную цену. Заведён баг BUG-5.",
                name="Bug Confirmation",
                attachment_type=allure.attachment_type.TEXT,
            )
            pytest.xfail("BUG-5: Сервер принимает отрицательную цену")

        assert resp.status_code == 400

    # ТК-7
    def test_create_negative_seller_id(self, api_client, valid_payload):
        payload = {**valid_payload, "sellerID": -1}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        if resp.status_code == 200:
            pytest.xfail("BUG-6: принимает отрицательный sellerID")
        assert resp.status_code == 400

    # ТК-8
    def test_create_invalid_json(self, api_client):
        resp = api_client.post(
            f"{BASE_URL}/api/1/item",
            data="{broken json}",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400

    # ТК-9
    def test_create_non_idempotent(self, api_client, valid_payload):
        ids = []
        for _ in range(2):
            resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload)
            ids.append(extract_item_id(resp.json()))
        assert ids[0] != ids[1]

    # ТК-10
    def test_create_long_name(self, api_client, valid_payload):
        payload = {**valid_payload, "name": "A" * 14000}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        if resp.status_code == 200:
            pytest.xfail("BUG-7: принимает имя длиной 14000 символов")
        assert resp.status_code == 400

    # ТК-11
    def test_create_high_price(self, api_client, valid_payload):
        payload = {**valid_payload, "price": 9999999999999999999}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        # BUG-8
        assert resp.status_code == 400

    # ТК-24
    def test_xss_injection(self, api_client, valid_payload):
        payload = {**valid_payload, "name": "<script>alert(1)</script>"}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        assert resp.status_code == 200

    # ТК-25
    def test_sql_injection(self, api_client, valid_payload):
        payload = {**valid_payload, "name": "'; DROP TABLE items;--"}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        assert resp.status_code == 200

    # ТК-26
    def test_performance(self, api_client, valid_payload):
        start = time.time()
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload)
        elapsed_ms = (time.time() - start) * 1000
        assert resp.status_code == 200
        if elapsed_ms > 300:
            pytest.xfail(f"BUG-11: Время ответа {elapsed_ms:.0f}мс > 300мс")

    # ТК-27
    def test_missing_content_type(self, api_client, valid_payload):
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={})
        if resp.status_code == 200:
            pytest.xfail("BUG-12: принимает запрос без Content-Type")
        assert resp.status_code in [400, 415]

    # ТК-34
    def test_empty_name(self, api_client, valid_payload):
        payload = {**valid_payload, "name": ""}
        resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload)
        assert resp.status_code == 400

    # ТК-35
    def test_put_method(self, api_client, valid_payload):
        resp = api_client.put(f"{BASE_URL}/api/1/item", json=valid_payload)
        assert resp.status_code in [404, 405]
