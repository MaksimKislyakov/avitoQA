import allure

from conftest import BASE_URL


class TestStatistics:
    # ТК-20
    @allure.title("ТК-20: Получение статистики существующего объявления")
    @allure.description("Проверяет, что статистика доступна для созданного объявления")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.story("Позитивный сценарий")
    def test_get_stat_existing(self, api_client, created_item):
        item_id = created_item["id"]

        with allure.step(f"Запрос статистики для ID: {item_id}"):
            resp = api_client.get(f"{BASE_URL}/api/1/statistic/{item_id}")

        with allure.step("Проверка статуса 200 OK и наличия метрик"):
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list) and len(data) > 0
            assert all(key in data[0] for key in ["likes", "viewCount", "contacts"])

    # ТК-21
    @allure.title("ТК-21: Запрос статистики для несуществующего ID")
    @allure.description(
        "Проверяет, что сервер возвращает 404 для статистики несуществующего объявления"
    )
    @allure.severity(allure.severity_level.NORMAL)
    @allure.story("Негативный сценарий")
    def test_get_stat_nonexistent(self, api_client):
        fake_id = "00000000-0000-0000-0000-000000000000"

        with allure.step(f"Запрос статистики для несуществующего ID: {fake_id}"):
            resp = api_client.get(f"{BASE_URL}/api/1/statistic/{fake_id}")

        with allure.step("Проверка статуса 404 Not Found"):
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
