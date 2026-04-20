import pytest
from conftest import BASE_URL

class TestStatistics:
    # ТК-20
    def test_get_stat_existing(self, api_client, created_item):
        item_id = created_item["id"]
        resp = api_client.get(f"{BASE_URL}/api/1/statistic/{item_id}")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list) and len(resp.json()) > 0

    # ТК-21
    def test_get_stat_nonexistent(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/statistic/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404

    # ТК-22
    def test_get_stat_invalid_format(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/1/statistic/invalid-format")
        assert resp.status_code in [400, 404]

    # ТК-30
    def test_get_stat_v2(self, api_client, created_item):
        item_id = created_item["id"]
        resp = api_client.get(f"{BASE_URL}/api/2/statistic/{item_id}")
        assert resp.status_code == 200