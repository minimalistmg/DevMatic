.PHONY: install test lint format clean build

install:
	pip install -r requirements.txt

test:
	pytest tests/

lint:
	flake8 src/
	black --check src/
	isort --check-only src/

format:
	black src/
	isort src/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:
	python -m build
