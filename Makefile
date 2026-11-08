PYTHON ?= python3
CONFIG ?= config.json
.PHONY: install run debug clean lint lint-strict test package
install:
	$(PYTHON) -m pip install -r requirements.txt
run:
	$(PYTHON) pac-man.py $(CONFIG)
debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)
clean:
	find . -type d \( -name __pycache__ -o -name .mypy_cache -o -name .pytest_cache \) -prune -exec rm -rf {} +
	rm -rf build dist
lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict --ignore-missing-imports
test:
	$(PYTHON) -m unittest discover -s tests -v
package:
	$(PYTHON) package.py
