Django Affect
=====================

Affect is a flagging engine which applies a flag value to requests based on defined criteria.

##Installing##
TODO

##Using in Views##
TODO

##Using in Templates##
TODO

##Settings##

`AFFECTED_NONENETRY_DOMAINS` - list of domains to exclude when deciding if a user if entering your site. `['example.com', 'www.example.net']` will exclude example.com and www.example.net from entry detection, (this would not exclude www.example.com or example.net)

There are a few ways coookies are set to insure persistence. These cookies affect how the cookies are stored
`AFFECTED_SECURE_COOKIE` - Encrypt affect cookies (default: `False`)
`AFFECTED_COOKIE` - string formattings to apply to criteria names for persistent flags, such as `dac_tester` for criteria called "tester". (default`'dac_%s'`)
`AFFECTED_TESTING_COOKIE` - string formatting to apply to criteria names when using testing functionality (default: `'dact_%s'`)

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
