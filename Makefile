.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3 features

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = [OPTIONAL] your-bucket-for-syncing-data (do not include 's3://')
PROFILE = default
PROJECT_NAME = kdd_air_quality
PYTHON_INTERPRETER = python3

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	python3 -m venv env
	bash env/bin/activate
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Make Dataset
data: 
	#Create data directories
	mkdir -p data/raw/Beijing
	mkdir -p data/raw/aq_station_merged
	mkdir -p data/interim

	# Download dataset provided by biendata
	wget -nc 'https://www.dropbox.com/s/mtyg1kitlt5k6h7/Beijing_grid_weather_station.csv?dl=1' -O ./data/raw/Beijing/Beijing_grid_weather_station.csv
	wget -nc 'https://www.dropbox.com/s/464rp6lhjgu0jv6/beijing_17_18_aq.csv?dl=1' -O ./data/raw/Beijing/beijing_17_18_aq.csv
	wget -nc 'https://www.dropbox.com/s/lv2i6tictta9pfq/beijing_201802_201803_aq.csv?dl=1' -O ./data/raw/Beijing/beijing_201802_201803_aq.csv
	wget -nc 'https://www.dropbox.com/s/jjta4addnyjndd8/beijing_17_18_meo.csv?dl=1' -O ./data/raw/Beijing/beijing_17_18_meo.csv
	wget -nc 'https://www.dropbox.com/s/94llgcr81u2tbg1/Beijing_historical_meo_grid.csv?dl=1' -O ./data/raw/Beijing/Beijing_historical_meo_grid.csv
	wget -nc 'https://www.dropbox.com/s/5lhxontpbfoyemi/Beijing_AirQuality_Stations_en.xlsx?dl=0' -O ./data/raw/Beijing/Beijing_AirQuality_Stations_en.xlsx
	wget -nc 'https://www.dropbox.com/s/nyy2ze7erho05jf/beijing_201802_201803_me.csv?dl=0' -O ./data/raw/Beijing/beijing_201802_201803_me.csv

	$(PYTHON_INTERPRETER) src/data/make_beijing_aq_data.py data/raw/Beijing data/interim/
	$(PYTHON_INTERPRETER) src/data/make_beijing_grid_data.py data/raw/Beijing data/interim/
	$(PYTHON_INTERPRETER) src/data/make_beijing_observed_data.py data/raw/Beijing data/interim/
	$(PYTHON_INTERPRETER) src/data/make_beijing_aq_stations.py data/raw/Beijing data/interim/
	$(PYTHON_INTERPRETER) src/data/make_weather_stations_list.py data/raw/Beijing data/interim/


## Create features
features:

	mkdir -p data/processed/donggaocun/pm25_train_test
	mkdir -p data/processed/donggaocun/pm10_train_test
	mkdir -p data/processed/donggaocun/O3_train_test
	
	$(PYTHON_INTERPRETER) src/features/merge_aq_weather_data.py data/interim data/interim/aq_station_merged
	$(PYTHON_INTERPRETER) src/features/impute_weather_data.py data/interim/aq_station_merged data/processed
	$(PYTHON_INTERPRETER) src/features/add_datepart.py data/processed data/processed
	$(PYTHON_INTERPRETER) src/features/process_categoricals.py data/processed data/processed
	$(PYTHON_INTERPRETER) src/features/timeseries_to_supervised.py data/processed data/processed
	$(PYTHON_INTERPRETER) src/features/generate_train_test.py data/processed data/processed/donggaocun

train:
	$(PYTHON_INTERPRETER) src/models/train_model.py data/processed/donggaocun models


predict:
	$(PYTHON_INTERPRETER) src/models/predict_model.py data/processed/donggaocun reports


## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Upload Data to S3
sync_data_to_s3:
ifeq (default,$(PROFILE))
	aws s3 sync data/ s3://$(BUCKET)/data/
else
	aws s3 sync data/ s3://$(BUCKET)/data/ --profile $(PROFILE)
endif

## Download Data from S3
sync_data_from_s3:
ifeq (default,$(PROFILE))
	aws s3 sync s3://$(BUCKET)/data/ data/
else
	aws s3 sync s3://$(BUCKET)/data/ data/ --profile $(PROFILE)
endif

## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_CONDA))
		@echo ">>> Detected conda, creating conda environment."
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	$(PYTHON_INTERPRETER) -m pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already intalled.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
