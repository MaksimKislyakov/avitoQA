import re
import pytest
from conftest import BASE_URL, extract_item_id

class TestSchemaValidation:
    # ТК-36
    def test_id_format(self, api_client, valid_payload):
        create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        item_id = extract_item_id(create_resp.json())
        assert item_id is not None
        assert re.match(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", item_id)

    # ТК-37
    def test_created_at_format(self, api_client, created_item):
        item_id = created_item["id"]
        get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        created_at = get_resp.json()[0].get("createdAt", "")
        assert isinstance(created_at, str)
        if "T" not in created_at or created_at.count("+0300") != 1:
            pytest.xfail("BUG-9: Неверный формат даты (ожидается ISO 8601)")

    # ТК-38
    def test_response_fields(self, api_client, created_item):
        item_id = created_item["id"]
        get_resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        data = get_resp.json()[0]
        expected_fields = {"id", "sellerId", "name", "price", "statistics", "createdAt"}
        assert set(data.keys()) == expected_fields, f"Лишние или недостающие поля: {set(data.keys())}"