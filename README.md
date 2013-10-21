Django Affect
=====================

Affect is a flagging engine which applies a flag value to requests based on defined criteria. While largely inspired by [django-waffle](https://github.com/jsocol/django-waffle), Affect focuses less on feature and rollout flags and more on changing user experience on a more detailed and longer term basis.

[![Build Status](https://travis-ci.org/ConsumerAffairs/django-affect.png?branch=master)](https://travis-ci.org/ConsumerAffairs/django-affect)
[![Coverage Status](https://coveralls.io/repos/ConsumerAffairs/django-affect/badge.png?branch=master)](https://coveralls.io/r/ConsumerAffairs/django-affect?branch=master)

Installing
----------
Install from [github](https://github.com/ConsumerAffairs/django-affect) with pip:

    pip install -e git@github.com:ConsumerAffairs/django-affect.git#django-affect

Or from PyPI:

    pip install django-affect

Add to installed apps and middleware

    INSTALLED_APPS = (
        ...
        'affected',
    )

    ...

    MIDDLEWARE_CLASSES = (
        ...
        'affect.middleware.AffectMiddleware',
    )

Affect expects that the Django Authentication middleware is in use as well.

Setup the database models using `./manage.py migrate affect` if you are using South, or `./manage.py syncdb` if you are not.

Using Affect
------------

###Creating Criteria and Flags###

Affect core functionality is broken into two models Criteria and Flags. Criteria are the decision making settings which are used to decide which Flags should be made "active". You can use the Django Admin to create new Criteria and Flags.

####Criteria fields####
`name` - used for storing and identifying this criteria. It is a slug field and is restricted to letters, numbers, underscores(_) and hyphens(-)

`flags` - flags objects to activate when this criteria is met

`persistent` - mark this if you would like all future requests to respect this criteria as the decision made for this request. Most useful when using `entry_url`, `referrer` and `query_args`. When `testing` args or `percent`-based assignment, persistent is implied.

`max_cookie_age` - the maximum age in seconds to store persistent or testing cookies. Default is 30 days, 0 or blank creates a session cookie. Age is updated on each request.

`everyone` - is active (yes) or inactive (no) for everyone, overriding all other options except persistent. Usually should be Unknown.

`testing` - allows you to use querystring args to override criteria status. Add `?dact_{{criteria_name}}=` with `1` to enable and `0` to disable. This is implied persistent and sets a cookie.

`percent` - enables criteria for a percentage of users. Implies persistent and sets a cookie.

`superusers` - enables for all Superusers.

`staff` - enables for all staff users.

`authenticated` - enables for all authenticated users.

`device_type` - attempt to detect and enable for users with a class of devices, mobile/table, desktop, or simple device/dumb phone. The practice of device detection is generally a bad idea. Use only for cases where end-users will not see results, such as server side logging. Use CSS and JS to detect features client-side for anything the user sees, they're up to the task.

`entry_url` - comma-separarted list of urls to enable criteria when user enters on them. Any domain other than that of the current request and any listed in the `AFFECTED_NONENTRY_DOMAINS` setting will be considered an entry.

`referrer` - comma-separated list of domains to enable criteria when referring page matchs.

`query_args` - a dictionary of key-value pairs to match in GET querystring. `{"foo": "bar"}` matches `?foo=bar`, `{'foo': '*'}` matches `?foo=<any value>`, and `{'foo': ['bar', 'baz']}` matches `?foo=bar` or `?foo=baz`. Key-values in querystring not defined here are ignored by Affect.

`groups` - user groups that enable criteria when user is a member of one or more of those groups.

`users` - sepecific users to enable criteria for.

`notes` - they're a good idea. Helps you remember what you intended.

####Flag fields####

`name` - identifying slug for this flag. Must be unique, using letters, numbers, underscores or hyphens only.

`active` - if not active, flag will not be enabled for anyone, regardless of criteria matches.

`conflicts` - other flags which conflict with this one. In the case that two flags affect similar features or functionality, mark them here and set `priority` accordingly.

`priority` - in event of `conflicts`, only the flag with the highest priority is enabled and all other conflicts ignored.

###"Looking" for Flags##

In Affect, Flags are the primary indicator of whether action should be taken by your code. Passing the `flag_is_affected` function the request object and flag name will tell you if the flag is enabled for this request.

    from affect import flag_is_affected

    def sample_view(request):
        if flag_is_affected(request, 'template_rev_b'):
            template = 'app/new_template.html'
        else:
            template = 'app/old_template.html'

###Settings###

`AFFECTED_NONENETRY_DOMAINS` - A list of domains to exclude when deciding if a user if entering your site. `['example.com', 'www.example.net']` will exclude example.com and www.example.net from entry detection, (this would not exclude www.example.com or example.net)

There are a few ways coookies are set to insure persistence. These cookies affect how the cookies are stored

`AFFECTED_SECURE_COOKIE`- Encrypt affect cookies (default: `False`)

`AFFECTED_COOKIE` - String formatting to apply to criteria names for persistent flags, such as `dac_tester` for criteria called "tester". (default: `'dac_%s'`)

`AFFECTED_TESTING_COOKIE` - String formatting to apply to criteria names when using testing functionality (default: `'dact_%s'`)

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

All pull requests should pass pep8 and pyflakes validation and have 100% test coverage and be developed in a separate feature branch.
