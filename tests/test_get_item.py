import pytest
from conftest import BASE_URL

class TestGetItem:
    # ТК-12
    def test_get_existing(self, api_client, created_item):
        item_id = created_item["id"]
        resp = api_client.get(f"{BASE_URL}/api/1/item/{item_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list) and len(data) > 0
        assert data[0]["id"] == item_id
        # BUG-9
        created_at = data[0].get("createdAt", "")
        if "T" not in created_at:
            pytest.xfail("BUG-9: createdAt не в формате ISO 8601")

    # ТК-13
    def test_get_nonexistent(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/item/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

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