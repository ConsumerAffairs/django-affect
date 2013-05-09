Django Affect
=====================

Affect is a flagging engine which applies a flag value to requests based on defined criteria.

##Installing##
TODO

##Using in Views##
TODO

##Using in Templates##
TODO

Developing
----------
Install requirements

    pip install fabric
    pip install -r requirements.txt

Setup db

    fab syncdb
    fab migrate

Start server

    fab serve

Using the Python shell

    fab shell

Running tests

    fab test

Creating South schema migrations

    fab schema
    fab migrate

All pull requests should pass pep8 and pyflakes validation and have 100% test coverage.
