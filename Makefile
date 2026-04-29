.PHONY: install run test help

VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest

help:
	@echo "Commands:"
	@echo "  make install  Create virtualenv and install dependencies"
	@echo "  make run      Start the window manager"
	@echo "  make test     Run the test suite"

install:
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) main.py

test:
	$(PYTEST) tests/ -v
