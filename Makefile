.PHONY: requirements

PROJECT_NAME = similar-day-forecasting-vae
PROJECT_HOME = $(HOME)/$(PROJECT_NAME)
PYTHON_INTERPRETER = python3

requirements:
	$(PYTHON_INTERPRETER) -m pip install --upgrade pip
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt
	$(PYTHON_INTERPRETER) -m pip install -e .

dotenv:
	echo "PROJECT_NAME=$(PROJECT_NAME)" > .env
	echo "PROJECT_HOME=$(PROJECT_HOME)" > .env

init-data:
	rm -rf $(PROJECT_HOME)/data
	mkdir -p $(PROJECT_HOME)/data/raw
	mkdir -p $(PROJECT_HOME)/data/processed
	mkdir -p $(PROJECT_HOME)/data/final

init-models:
	rm -rf $(PROJECT_HOME)/models
	mkdir -p $(PROJECT_HOME)/models

init:
	make init-data
	make init-models

nem-data:
	git clone https://github.com/ADGEfficiency/nem-data
	pip install -r nem-data/requirements.txt
	python nem-data/setup.py install

dl:
	nem --reports demand --start 2015-01 --end 2019-12
	cp -r ~/nem-data $(PROJECT_HOME)/data/raw

pipeline:
	python3 src/data_pipeline.py

baselines:
	python3 src/baselines.py

app:
	streamlit run src/app.py > /dev/null 2>&1 &
