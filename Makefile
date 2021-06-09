# ----------------------------------
#          INSTALL & TEST
# ----------------------------------
install_requirements:
	@pip install -r requirements.txt

check_code:
	@flake8 scripts/* StarFish/*.py

black:
	@black scripts/* StarFish/*.py

test:
	@coverage run -m pytest tests/*.py
	@coverage report -m --omit="${VIRTUAL_ENV}/lib/python*"

ftest:
	@Write me

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr StarFish-*.dist-info
	@rm -fr StarFish.egg-info

install:
	@pip install . -U

all: clean install test black check_code

count_lines:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./scripts -name '*-*' -exec  wc -l {} \; | sort -n| awk \
		        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''
	@find ./tests -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

# ----------------------------------
#      UPLOAD PACKAGE TO PYPI
# ----------------------------------
PYPI_USERNAME=<AUTHOR>
build:
	@python setup.py sdist bdist_wheel

pypi_test:
	@twine upload -r testpypi dist/* -u $(PYPI_USERNAME)

pypi:
	@twine upload dist/* -u $(PYPI_USERNAME)

# ----------------------------------
#         HEROKU COMMANDS
# ----------------------------------

streamlit:
	-@streamlit run app.py

heroku_login:
	-@heroku login

heroku_create_app:
	-@heroku create ${APP_NAME}

deploy_heroku:
	-@git push heroku master
	-@heroku ps:scale web=1

# ----------------------------------
#         STREAMLIT COMMANDS
# ----------------------------------

run_streamlit:
	streamlit run app.py

# project id - replace with your GCP project id
PROJECT_ID=starfish-316120

# bucket name - replace with your GCP bucket name
BUCKET_NAME=starfish-databases

# choose your region from https://cloud.google.com/storage/docs/locations#available_locations
REGION=europe-west1

set_project:
	@gcloud config set project ${PROJECT_ID}

create_bucket:
	@gsutil mb -l ${REGION} -p ${PROJECT_ID} gs://${BUCKET_NAME}

# File to upload to gcp
LOCAL_PATH_TOP="StarFish/data/top_streams_2450.csv"
LOCAL_PATH_STREAMERS="StarFish/data/streamers_clean.csv"
LOCAL_PATH_SOCIALS="StarFish/data/socials_clean.csv"
LOCAL_PATH_GAMES="StarFish/data/games_clean.csv"

# Bucket directory in which to store the uploaded file (`data` is an arbitrary name that we choose to use)
BUCKET_FOLDER=scraped_data

# Name for the uploaded file inside of the bucket (we choose not to rename the file that we upload)
BUCKET_FILE_NAME_TOP=$(shell basename ${LOCAL_PATH_TOP})
BUCKET_FILE_NAME_STREAMERS=$(shell basename ${LOCAL_PATH_STREAMERS})
BUCKET_FILE_NAME_SOCIALS=$(shell basename ${LOCAL_PATH_SOCIALS})
BUCKET_FILE_NAME_GAMES=$(shell basename ${LOCAL_PATH_GAMES})

upload_data:
	@gsutil cp ${LOCAL_PATH_TOP} gs://${BUCKET_NAME}/${BUCKET_FOLDER}/${BUCKET_FILE_NAME_TOP}
	@gsutil cp ${LOCAL_PATH_STREAMERS} gs://${BUCKET_NAME}/${BUCKET_FOLDER}/${BUCKET_FILE_NAME_STREAMERS}
	@gsutil cp ${LOCAL_PATH_SOCIALS} gs://${BUCKET_NAME}/${BUCKET_FOLDER}/${BUCKET_FILE_NAME_SOCIALS}
	@gsutil cp ${LOCAL_PATH_GAMES} gs://${BUCKET_NAME}/${BUCKET_FOLDER}/${BUCKET_FILE_NAME_GAMES}

