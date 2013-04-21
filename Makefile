.PHONY: test install deploy run teams stage


install: venv
	venv/bin/pip install -r requirements.txt

venv:
	virtualenv --python=python3.3 venv

test:
	venv/bin/flake8 tests vogeltron
	venv/bin/nosetests tests

teams:
	venv/bin/python -m vogeltron.teams

stage:
	venv/bin/python -m vogeltron.deploy reddits/test.json

deploy:
	venv/bin/python -m vogeltron.deploy reddits/subs.json

run:
	heroku run python -m vogeltron.bot --app sfgiants-staging
