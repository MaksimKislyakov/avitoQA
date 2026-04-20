import pytest
from conftest import BASE_URL

class TestSellerItems:
    # ТК-16
    def test_get_seller_items(self, api_client, valid_payload):
        sid = valid_payload["sellerID"]
        api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        api_client.post(f"{BASE_URL}/api/1/item", json=valid_payload, headers={"Content-Type": "application/json"})
        resp = api_client.get(f"{BASE_URL}/api/1/{sid}/item")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list) and len(resp.json()) >= 2

    # ТК-17
    def test_get_empty_seller(self, api_client, unique_seller_id):
        resp = api_client.get(f"{BASE_URL}/api/1/{unique_seller_id}/item")
        assert resp.status_code == 200
        assert resp.json() == []

    # ТК-18
    def test_get_negative_seller_id(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/-1/item")
        if resp.status_code == 200:
            pytest.xfail("BUG-10: принимает отрицательный sellerID в URL")
        assert resp.status_code == 400

    # ТК-19
    def test_get_invalid_seller_id_format(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/abc-def/item")
        assert resp.status_code in [400, 404]