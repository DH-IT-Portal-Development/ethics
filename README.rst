====
ETCL
====

Ethical Committee web application in Django

Introduction
------------

This Django_ project allows a user to apply a research project for ethical review.
It was custom-tailored for the `Ethical Committee Linguistics`_ (ETCL) of `Utrecht University`_.

Installation
------------

Installation of this Django project is quite straightforward:

- Clone the git repository
- Install the requirements (in a virtualenv) using `pip install -r requirements.txt`.
- Modify the settings file (`etcl/settings.py`) to your liking.
- Run the database migrations using `python manage.py migrate`.
- Load all fixtures using `python manage.py loaddata`.
- Create a superuser (`python manage.py create_superuser`) and add additional users in the admin interface
- You are ready to roll!

For deployment on a virtual machine, there is a Puppet module available on request.

Structure
---------

This Django project consists of ten apps that can be divided into three categories:

- Core
    - *etcl*: Main directory with settings and a WSGI configuration.
    - *core*: Core functionality, reusable models, views, forms and templates.

- Proposals
    - *proposals*: Main application that binds together all applications below. Allows participants to give general information on their study.
    - *studies*: Allows users to add more in-detail information on their study.
    - *observations*: Allows users to specify the observation part of their study (if applicable).
    - *interventions*: Allows users to specify the intervention part of their study (if applicable).
    - *tasks*: Allows users to specify tasks in their study (if applicable). Tasks can be grouped in one or more sessions.
    - *reviews*: Allows the committee to review proposals.

- Feedback
    - *feedback*: Allows users to give feedback on the application: with what parts did they struggle?
    - *faqs*: Provides users with answers to frequently asked questions about the application.

Tests
-----

The project contains a test bed that mainly focuses on the server side.
The tests can be run using `python manage.py test`.

Language
--------

The main language of this web application is Dutch, as it's aimed towards the mostly avid Dutch-speaking researchers of Utrecht University.
However, since October 2016, there is a full English translation available, compiled by `Anna Asbury`_.
Translations in other languages are welcome, of course.
Translations can be easily created using `python manage.py makemessages` and edited using e.g. `Poedit`_.

Tooling
-------

The project uses a few tools to simplify the development workflow:

- `pip-tools`_ for computing requirements, see `requirements.in`.
- `Travis CI`_ for automatically building and running of tests, see `.travis.yml`.
- `coverage.py`_ for test coverage reports, install coverage.py and then run `coverage run --source='.' manage.py test` and `coverage html` to generate the coverage report.

.. _Django: https://www.djangoproject.com/
.. _Ethical Committee Linguistics: https://etcl.wp.hum.uu.nl
.. _Utrecht University: https://www.uu.nl
.. _Anna Asbury: http://www.annaasbury.com/
.. _Poedit: https://poedit.net/
.. _pip-tools: https://github.com/jazzband/pip-tools
.. _Travis CI: https://travis-ci.org/
.. _coverage.py: http://coverage.readthedocs.io/
