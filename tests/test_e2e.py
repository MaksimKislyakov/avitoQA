import pytest
from conftest import BASE_URL, extract_item_id

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