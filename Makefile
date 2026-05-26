.PHONY: setup ingest demo test clean
PY ?= python3
export PYTHONPATH := src

setup:
	$(PY) -m pip install -e ".[dev]"

ingest:
	$(PY) -m dmaic_coach.rag.ingest

demo: ingest
	$(PY) -m dmaic_coach.cli --demo

run: ingest
	$(PY) -m dmaic_coach.cli

test:
	$(PY) -m pytest -q

clean:
	rm -f kb.db
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
