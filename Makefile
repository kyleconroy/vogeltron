.PHONY: test install deploy run teams

install: venv
	venv/bin/pip install -r requirements.txt

venv:
	virtualenv --python=python3.3 venv

test:
	venv/bin/flake8 tests vogeltron
	venv/bin/nosetests tests

teams:
	. venv/bin/activate; python generate_teams.py

deploy:
	git push staging master

run:
	heroku run python -m vogeltron.bot --app sfgiants-staging
