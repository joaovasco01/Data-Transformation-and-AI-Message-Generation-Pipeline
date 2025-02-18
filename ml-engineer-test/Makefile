

.ONESHELL:
venv:
	python3 -m venv venv
	source venv/bin/activate && \
	python -m pip install --upgrade pip setuptools wheel pipenv && \
	python -m pip install -e .

# transform
.PHONY: transform
transform:
	message transform