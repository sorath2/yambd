WORKDIR = api_yamdb
MANAGE = python $(WORKDIR)/manage.py
DEVREQS = dev-requirements.txt
REQS = requirements.txt

deps:
	pip install --upgrade pip pip-tools
	pip-compile --output-file $(REQS) --resolver=backtracking pyproject.toml

dev-deps: deps
	pip-compile --extra=dev --output-file $(DEVREQS) --resolver=backtracking pyproject.toml

gen-schema:
	$(MANAGE) spectacular --color --file $(WORKDIR)/schema.yml

install:
	python -m venv venv 
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r $(DEVREQS)
	venv/bin/$(MANAGE) migrate

install-deps: deps
	pip-sync $(REQS)

install-dev-deps: install-deps dev-deps
	pip-sync $(DEVREQS)

run:
	venv/bin/$(MANAGE) runserver

style:
	black $(WORKDIR)
	isort $(WORKDIR)
	flake8 $(WORKDIR)
	mypy $(WORKDIR)
	pymarkdown scan .

test:
	pytest
