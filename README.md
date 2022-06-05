Eva
----

An evaluation system written in Python/Django.

Pre-requisites
--------------
- Python 3.6
- poetry  (for dependency management)
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Installation
------------
- Clone the repository
```
git clone https://github.com/Beyond5/eva
```
- Install using `poetry`
```
cd eva
poetry install
```

Run server
----------
- Open the environment using `poetry shell`
- Run the server using `python manage.py runserver`
```
poetry shell
python manage.py runserver
```