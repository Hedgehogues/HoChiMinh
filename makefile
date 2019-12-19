PYTHONPATH=.
TESTS=tests/
LOG_PATH=.log/

ifndef PYTHON
	PYTHON=python
endif
ifndef PYTEST
	PYTEST=pytest
endif
ifndef PIP
	PIP=pip
endif
ifndef GIT
	GIT=git
endif
ifndef TEST_SUBFOLDER
	TEST_SUBFOLDER=./
endif


ENVS=PYTHONPATH=${PYTHONPATH} ENV_FILE=${ENV_FILE}


run:
	$(info storage starting...)
	$(info $(ENVS))
	$(info ${STORAGE_ENV_FILE})
	$(ENVS) $(PYTHON) app.py

test:
	$(info integration tests running...)
	$(info $(ENVS))
	$(info ${TESTS}${TEST_SUBFOLDER})
	$(ENVS) $(PYTEST) -v -l --disable-warnings ${TESTS}${TEST_SUBFOLDER}

deps:
	$(info public dependencies installing...)
	$(info $(ENVS))
	$(PIP)  install --upgrade pip
	$(PIP) install -r requirements
