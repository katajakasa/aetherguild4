# Aetherguild.net v4

Gaming guild website.

Requirements
------------

* Python 3.11.x (`https://www.python.org/`)
* Poetry package manager (`https://python-poetry.org/docs/#installation`)
* PostgreSQL or SQLite for database. SQLite should be fine for testing
  and development purposes. MariaDB/MySQL is not tested or supported.
* Redis 5 or later (production only, not required for development)

Installing stuff for development
--------------------------------

1. Install the dependencies and clone this project.
2. Copy `settings.py-dist` to `settings.py`. Change as needed. `settings.py` should never be added to
   git, as it may contain secrets.
3. Set up environment with poetry `poetry env use 3.11`.
4. Install packages with poetry `poetry install --no-root --sync`.
5. Make sure your database is set up and configured in settings.py, and then run database
   migrations to set up initial data `python manage.py migrate`.
6. Create a superuser so that you can access the admin `python manage.py createsuperuser`.
7. That's all. Now just start local dev server by running `python manage.py runserver`.

Note that some background operations use celery. It can be started with following:
`python -m celery -A aether worker -l info --autoscale 2,1`

Running in production
---------------------

Use uvicorn (ASGI): `uvicorn aether.asgi:application`

Deploying
---------

When deploying, the following steps need to be run:

```
python manage.py collectstatic --noinput
python manage.py compress
python manage.py migrate
```

After this, restart the WSGI/ASGI runner.

Running tests
-------------

Just do `pytest` in the main directory :)

To also get coverage, do `pytest --cov=Instanssi`

Also, you can run tests in parallel using `pytest -n 4`.

Production deps
---------------

To install in production, remember to generate a new requirements.txt file.

`poetry export --with=runtime -f requirements.txt -o requirements.txt`.

License
-------
MIT. Please refer to `LICENSE` for more information.