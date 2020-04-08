.PHONY: setup
setup:
	pip install -r requirements.txt
	pip install --editable .

.PHONY: dist
dist:
	python3 setup.py sdist bdist_wheel

.PHONY: clean
clean:
	rm -fr build dist *.egg-info

PHONY: black
black:
	black --skip-string-normalization wfp_food_security_alerts *.py

.PHONY: black-check
black-check:
	black --check --skip-string-normalization wfp_food_security_alerts *.py

.PHONY: flake8
flake8:
	flake8 --ignore=E501,E402,W503 wfp_food_security_alerts *.py

.PHONY: mypy
mypy:
	mypy wfp_food_security_alerts

.PHONY: pylint
pylint:
	pylint wfp_food_security_alerts *.py

.PHONY: pycodestyle
pycodestyle:
	pycodestyle --ignore=E501,W503,E402,E701 wfp_food_security_alerts *.py

.PHONY: check
check: black-check flake8 mypy pylint pycodestyle

.PHONY:
venv:
	python3 -m venv venv

.PHONY: test
test:
	py.test -p no:warnings

.PHONY: coverage
coverage:
	coverage run -m py.test -p no:warnings
	coverage report
	coverage html
	coverage xml

