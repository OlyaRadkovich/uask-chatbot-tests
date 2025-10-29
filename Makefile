.PHONY: help setup run smoke ui ai sec headless en ar report clean

# Default target
.DEFAULT_GOAL := help

SHELL := /bin/bash
PY := python3
PIP := pip3
TEST := pytest

help:
    @echo "AskBot E2E Tests"
    @echo "----------------"
    @echo "make setup        # create venv and install deps"
    @echo "make run          # run full test suite"
    @echo "make smoke        # quick smoke subset"
    @echo "make ui           # UI-oriented tests"
    @echo "make ai           # AI response tests"
    @echo "make sec          # security suite"
    @echo "make headless     # run in headless mode"
    @echo "make en|ar        # force language"
    @echo "make report       # HTML report"
    @echo "make clean        # cleanup artifacts"

setup:
    @echo "[setup] preparing virtualenv"
    $(PY) -m venv .venv || true
    @echo "[setup] installing requirements"
    $(PIP) install --upgrade pip
    $(PIP) install -r requirements.txt
    @echo "[setup] done. activate: source .venv/bin/activate"

run:
    $(TEST) -v

smoke:
    $(TEST) -m smoke -q

ui:
    $(TEST) -m ui -v

ai:
    $(TEST) -m ai_response -v

sec:
    $(TEST) -m security -v

headless:
    $(TEST) -v --headless

en:
    $(TEST) -v --language=en
ar:
    $(TEST) -v --language=ar

report:
    $(TEST) -q --html=reports/test_report.html --self-contained-html
    @echo "report: reports/test_report.html"

clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    rm -rf .pytest_cache .coverage htmlcov/ 2>/dev/null || true
    rm -rf reports/*.html reports/logs/*.log 2>/dev/null || true
    @echo "clean: done"
