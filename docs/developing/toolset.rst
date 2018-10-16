Toolset
=======

The project uses a few tools to simplify the development workflow:

- `pip-tools`_ for computing requirements, see `requirements.in`.
- `Travis CI`_ for automatically building and running of tests, see `.travis.yml`.
- `coverage.py`_ for test coverage reports, install coverage.py and then run `coverage run --source='.' manage.py test` and `coverage html` to generate the coverage report.
- `requires.io`_ for critical update notifications

.. _pip-tools: https://github.com/jazzband/pip-tools
.. _Travis CI: https://travis-ci.org/
.. _coverage.py: http://coverage.readthedocs.io/
.. _requires.io: https://requires.io