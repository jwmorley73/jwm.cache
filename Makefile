.PHONY = clean format test

venv=./.venv
python=$(venv)/bin/python

clean:
	rm -rf **/*.egg-info

test: |
	$(python) -m pytest --cov=jwm.cache --cov=jwm._cache .
	$(python) -m coverage html


format:
	$(python) -m isort --profile=black ./src ./tests && $(python) -m black ./src ./tests
