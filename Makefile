VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate

help:
	@echo "Makefile help. Your options are:"
	@echo "clean - remove build and Python file artifacts"
	@echo "install - install basic dependencies with venv"
	@echo "venv_lint - check style with flake8 and mypy with venv"
	@echo "venv_test - run tests with venv"

clean:
	rm -rf $(VENV_NAME)
	rm -rf *.egg-info
	find . -name __pycache__ -exec rm -rf {} \;
	find . -name .mypy_cache -exec rm -rf {} \;

install:
	python3 -m venv $(VENV_NAME);
	$(VENV_ACTIVATE)
	${VENV_NAME}/bin/python -m pip install -r requirements.txt
	${VENV_NAME}/bin/python -m pip install .
	@touch $(VENV_NAME)/bin/activate

venv_activate:
	$(VENV_ACTIVATE)

venv_lint: venv_activate
	flake8 --config=flake8.ini ./src ./tests && mypy --config-file mypy.ini -p src

venv_test: venv_activate
	@echo "TODO: implement tests"

