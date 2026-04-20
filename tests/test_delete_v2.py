import pytest
from conftest import BASE_URL, extract_item_id

class TestDeleteV2:
    # ТК-29
    def test_delete_existing(self, api_client, valid_payload):
        create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        item_id = extract_item_id(create_resp.json())

        del_resp = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        assert del_resp.status_code == 200

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
    def test_delete_twice(self, api_client, valid_payload):
        create_resp = api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        item_id = extract_item_id(create_resp.json())

        api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        resp = api_client.delete(f"{BASE_URL}/api/2/item/{item_id}")
        assert resp.status_code == 404