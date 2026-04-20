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