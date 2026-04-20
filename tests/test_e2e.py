import pytest
from conftest import BASE_URL, extract_item_id
import random

class TestE2E:
    # ТК-23
    def test_full_lifecycle(self, api_client, valid_payload):
        # 1. Создание
        post_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        assert post_resp.status_code == 200
        item_id = extract_item_id(post_resp.json())
        seller_id = valid_payload["sellerID"]

        # 2. Получение по ID
        get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        assert get_resp.status_code == 200

        # 3. Получение статистики
        stat_resp = api_client.get(f"{BASE_URL}/api/1/statistic/{item_id}")
        assert stat_resp.status_code == 200

        # 4. Проверка в списке продавца
        list_resp = api_client.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert list_resp.status_code == 200
        assert any(item.get("id") == item_id for item in list_resp.json())

        # 5. Удаление
        del_resp = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        assert del_resp.status_code == 200
    #ТК-24
    def test_cross_version_consistency(self, api_client, valid_payload):
        # 1. Создаем объявление через API v1
        post_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        assert post_resp.status_code == 200
        item_id = extract_item_id(post_resp.json())

        # 2. Проверяем, что объект доступен через v1
        get_v1 = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        assert get_v1.status_code == 200

        # 3. Удаляем объект через API v2
        del_v2 = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        assert del_v2.status_code == 200

        # 4. Проверяем, что объект исчез из хранилища и недоступен через v1
        get_v1_after = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        assert get_v1_after.status_code == 404

        # 5. Проверяем, что статистика тоже пропала
        stat_v1_after = api_client.get(f"{BASE_URL}/api/1/statistic/{item_id}")
        if stat_v1_after.status_code == 200:
            pytest.xfail("BUG-11: сохранение статистики после удаления объявления")
        assert stat_v1_after.status_code == 404
    #ТК-25
    def test_seller_list_consistency_after_deletion(self, api_client, valid_payload):
        seller_id = valid_payload["sellerID"]

        # 1. Создаем два объявления для одного продавца (копируем payload, чтобы не мутировать оригинал)
        payload_a = {**valid_payload, "name": "Товар А"}
        payload_b = {**valid_payload, "name": "Товар Б", "price": valid_payload["price"] + 100}

        ids = []
        for payload in [payload_a, payload_b]:
            resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload, headers={"Content-Type": "application/json"})
            assert resp.status_code == 200
            ids.append(extract_item_id(resp.json()))

        # 2. Проверяем список продавца (должно быть >= 2)
        list_resp = api_client.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert list_resp.status_code == 200
        initial_items = list_resp.json()
        assert len(initial_items) >= 2

        # 3. Удаляем первый товар через API v2
        del_resp = api_client.delete(f"{BASE_URL}/api/2/item/{ids[0]}")
        assert del_resp.status_code == 200

        # 4. Проверяем список продавца снова
        list_resp_after = api_client.get(f"{BASE_URL}/api/1/{seller_id}/item")
        assert list_resp_after.status_code == 200
        remaining_items = list_resp_after.json()
        
        # Удаленного товара быть не должно
        assert not any(item["id"] == ids[0] for item in remaining_items)
        # Второй товар должен остаться
        assert any(item["id"] == ids[1] for item in remaining_items)
    #ТК-26
    def test_statistics_v1_v2_consistency(self, api_client, valid_payload):
        # 1. Создаем объявление
        post_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        assert post_resp.status_code == 200
        item_id = extract_item_id(post_resp.json())

        # 2. Запрашиваем статистику через API v1
        stat_v1 = api_client.get(f"{BASE_URL}/api/1/statistic/{item_id}")
        assert stat_v1.status_code == 200
        v1_data = stat_v1.json()
        if isinstance(v1_data, list) and v1_data:
            v1_data = v1_data[0]

        # 3. Запрашиваем статистику через API v2
        stat_v2 = api_client.get(f"{BASE_URL}/api/2/statistic/{item_id}")
        assert stat_v2.status_code == 200
        v2_data = stat_v2.json()
        if isinstance(v2_data, list) and v2_data:
            v2_data = v2_data[0]

        # 4. Сравниваем метрики: они должны быть идентичны
        assert v1_data.get("likes") == v2_data.get("likes")
        assert v1_data.get("viewCount") == v2_data.get("viewCount")
        assert v1_data.get("contacts") == v2_data.get("contacts")
    #ТК-27
    def test_seller_data_isolation(self, api_client, valid_payload):
        # 1. Создаем товар для Продавца А
        seller_a_id = valid_payload["sellerID"]
        item_a_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        assert item_a_resp.status_code == 200
        item_a_id = extract_item_id(item_a_resp.json())

        # 2. Создаем товар для Продавца Б (генерируем ДРУГОЙ ID, отличный от seller_a_id)
        seller_b_id = random.randint(111111, 999999)
        while seller_b_id == seller_a_id:
            seller_b_id = random.randint(111111, 999999)

        payload_b = {**valid_payload, "sellerID": seller_b_id, "name": "Товар Продавца Б"}
        item_b_resp = api_client.post(f"{BASE_URL}/api/1/item", json=payload_b, headers={"Content-Type": "application/json"})
        assert item_b_resp.status_code == 200
        item_b_id = extract_item_id(item_b_resp.json())

        # 3. Проверяем список Продавца А
        list_a = api_client.get(f"{BASE_URL}/api/1/{seller_a_id}/item").json()
        assert any(item["id"] == item_a_id for item in list_a), "Товар А должен быть в списке продавца А"
        assert not any(item["id"] == item_b_id for item in list_a), "Товар Б НЕ должен попадать в список продавца А"

        # 4. Проверяем список Продавца Б
        list_b = api_client.get(f"{BASE_URL}/api/1/{seller_b_id}/item").json()
        assert any(item["id"] == item_b_id for item in list_b), "Товар Б должен быть в списке продавца Б"
        assert not any(item["id"] == item_a_id for item in list_b), "Товар А НЕ должен попадать в список продавца Б"