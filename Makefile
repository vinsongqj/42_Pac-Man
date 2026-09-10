.PHONY: install run debug clean lint lint-strict


install:
	@echo "Installing dependencies..."
	@uv sync
	@echo "Dependencies installed!"
run:
	uv run pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .mypy_cache -exec rm -rf {} +
	@rm -rf venv

lint:
	@flake8 . --exclude=./venv,venv,*/venv/*,.venv
	@mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude='^venv/'

lint-strict:
	@flake8 . --exclude=./venv,venv,*/venv/*,.venv
	@mypy . --strict --exclude='^venv/'

help:
	@echo "Available commands:"
	@echo "   install     - Install dependencies"
	@echo "   run         - Run the game"
	@echo "   debug       - Run in debug mode"
	@echo "   clean       - Remove all build files"
	@echo "   lint        - Run flake8 and mypy linters"
	@echo ""
