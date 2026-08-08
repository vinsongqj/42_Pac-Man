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
