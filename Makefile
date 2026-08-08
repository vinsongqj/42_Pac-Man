.PHONY: install run debug clean lint lint-strict


install:
	@echo "Installing dependencies..."
	@pip install -q -r requirements.txt
	@echo "Dependencies installed!"
run:
	python3 pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type d -name .mypy_cache -exec rm -rf {} +
	@rm -rf venv

lint:
	flake8 . --exclude=venv
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude='^venv/'

help:
	@echo "Available commands:"
	@echo "   install     - Install dependencies"
	@echo "   run         - Run the game"
	@echo "   debug       - Run in debug mode"
	@echo "   clean       - Remove all build files"
	@echo "   lint        - Run flake8 and mypy linters"
	@echo ""
	@echo "First time setup:"
	@echo "   1. python3 -m venv venv"
	@echo "   2. source venv/bin/activate"
	@echo "   3. make install"
	@echo "   4. make run"