.DEFAULT_GOAL := default

.PHONY: default
default: setup build

.PHONY: setup
setup:
	poetry install

.PHONY: check
check: types lint
	poetry run black --check .

.PHONY: types
types:
	poetry run mypy ecsctl || exit 0

.PHONY: lint
lint:
	poetry run flake8

.PHONY: fromat
format:
	poetry run black .


.PHONY: build
build: build-wheel
	poetry run pyinstaller ./ecsctl/__main__.py --onefile --name ecsctl

.PHONY: build-wheel
build-wheel:
	poetry build

.PHONY: install
install:
	@mkdir -p ~/.local/bin
	cp dist/ecsctl ~/.local/bin

poetryversion:
	poetry version $(version)
	poetry install
	
version: poetryversion
	$(eval NEW_VERS := $(shell cat pyproject.toml | grep "^version = \"*\"" | cut -d'"' -f2))
	sed -i "s/__version__ = .*/__version__ = \"$(NEW_VERS)\"/g" ecsctl/__init__.py
