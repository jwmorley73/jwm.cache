.PHONY = clean format

venv=./.venv
python=$(venv)/bin/python

clean:
	rm -rf **/*.egg-info

format:
	$(python) -m isort --profile=black ./src && $(python) -m black ./src
