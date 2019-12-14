check-virtual-env:
	@echo virtual-env: $${VIRTUAL_ENV?"Please run in a virtual-env"}

.PHONY: bootstrap
bootstrap: check-virtual-env
	pip install -U pip
	pip install -r requirements.txt
	cd ephem && ./get-ephem.sh

.PHONY: run
run: check-virtual-env
run: sotp.py
	FLASK_APP=$< FLASK_DEBUG=1 flask run
