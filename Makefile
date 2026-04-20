.PHONY: lint
lint:
	black .
	mypy .
	ruff check . --fix
	ruff check .

.PHONY: tests
tests:
	pytest tests/ -v

.PHONY: tests_allure
tests_allure:
	pytest tests/ --alluredir=allure-results -v
	allure generate allure-results -o allure-report --clean
	allure open allure-report
