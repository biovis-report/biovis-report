.PHONY: all install-dev test docs release clean-pyc

all: test

install-dev:
	pip install -e .[dev]

test: clean-pyc install-dev
	pytest

docs: clean-pyc
	cd docs && sphinx-apidoc -o source/api ../biovis_report
	cd docs && sphinx-apidoc -o source/api ../biovis_media_extension
	cd docs && $(MAKE) html

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
