.PHONY: install build run debug clean lint lint-strict


install:
	@echo "Installing dependencies..."
	@uv sync
	@echo "Dependencies installed!"

build:	install
	@uv run pyinstaller --clean --noconfirm pac-man.spec
	@cp config.json dist/config.json

run:	install
	uv run pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .mypy_cache -exec rm -rf {} +
	@rm -rf venv .venv build dist highscores.json

lint:
	@flake8 . --exclude=./venv,venv,*/venv/*,.venv
	@mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude '^venv/' --explicit-package-bases src pac-man.py

lint-strict:
	@flake8 . --exclude=./venv,venv,*/venv/*,.venv
	@mypy --strict --exclude='^venv/' --explicit-package-bases src pac-man.py
