
init-db:
	set FLASK_APP=laboratory && \
	set FLASK_ENV=development && \
	flask init-db

run:
	set FLASK_APP=laboratory && \
	set FLASK_ENV=development && \
	flask run