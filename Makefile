.DEFAULT_GOAL := default

.PHONY: default
default: setup build

.PHONY: setup
setup:
	poetry install

.PHONY: check
check: types
	poetry run black --check .

.PHONY: types
types:
	poetry run mypy ecsctl

.PHONY: fromat
format:
	poetry run black .


.PHONY: build
build:
	poetry run pyinstaller ./ecsctl/__main__.py --onefile --name ecsctl

.PHONY: install
install:
	@mkdir -p ~/.local/bin
	cp dist/ecsctl ~/.local/bin
