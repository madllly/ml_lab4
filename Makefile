#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_NAME = yuminov-lab
PYTHON_VERSION = 3.10
PYTHON_INTERPRETER = python
DOWNLOAD_SCRIPT=lab3/scripts/download_from_s3.py
DOWNLOAD_PATH=lab3/titanic_processed.csv
#################################################################################
# COMMANDS                                                                      #
#################################################################################

setup:
	poetry install
	docker-compose up -d

build-trainer-image:
	docker build -f Dockerfile.train -t trainer:latest .

upload-data:
	poetry run python lab3/scripts/create_bucket.py ; \
	poetry run python lab3/scripts/upload_to_s3.py --bucket data-bucket --file_path lab3/titanic.csv

process-data:
	poetry run python lab3/scripts/process_data.py --bucket data-bucket --input_path titanic.csv --output_path titanic_processed.csv

download processed-data:
	poetry run python $(DOWNLOAD_SCRIPT) --bucket data-bucket --object_name titanic_processed.csv --download_path $(DOWNLOAD_PATH)

run-experiments:
	bash lab3/scripts/run_experiment.sh lab3/config_grid.json experiment_name

upload-results:
	poetry run python lab3/scripts/upload_experiment_results.py --bucket data-bucket --directory output



## Delete all compiled Python files
.PHONY: clean
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8 and black (use `make format` to do formatting)
.PHONY: lint
lint:
	flake8 lab3 
	isort --check --diff --profile black lab3
	black --check --config pyproject.toml lab3

## Format source code with black
.PHONY: format
format:
	black --config pyproject.toml lab3




## Set up python interpreter environment
.PHONY: create_environment
create_environment:
	@bash -c "if [ ! -z `which virtualenvwrapper.sh` ]; then source `which virtualenvwrapper.sh`; mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); else mkvirtualenv.bat $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER); fi"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"




#################################################################################
# PROJECT RULES                                                                 #
#################################################################################


## Make Dataset
.PHONY: data
data: requirements
	$(PYTHON_INTERPRETER) src/dataset.py


#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys; \
lines = '\n'.join([line for line in sys.stdin]); \
matches = re.findall(r'\n## (.*)\n[\s\S]+?\n([a-zA-Z_-]+):', lines); \
print('Available rules:\n'); \
print('\n'.join(['{:25}{}'.format(*reversed(match)) for match in matches]))
endef
export PRINT_HELP_PYSCRIPT

help:
	@$(PYTHON_INTERPRETER) -c "${PRINT_HELP_PYSCRIPT}" < $(MAKEFILE_LIST)
