RUNFLAGS="--host=0.0.0.0"

default: run

check-virtual-env:
	@echo virtual-env: $${VIRTUAL_ENV?"Please run in a virtual-env"}

.PHONY: init
init: check-virtual-env
	pip install -U pip setuptools
	pip install -r requirements.txt
	cd ephem && ./download-ephem.sh

.PHONY: run
run: check-virtual-env
run: sotp.py
	FLASK_APP=$< FLASK_DEBUG=1 flask run $(RUNFLAGS)

.PHONY: notebook
notebook: check-virtual-env
	jupyter notebook .
