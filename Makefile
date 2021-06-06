.PHONY: check
check:
	poetry run black --check .

.PHONY: fromat
format:
	poetry run black .
