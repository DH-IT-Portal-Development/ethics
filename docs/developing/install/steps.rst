******************
Installation Steps
******************

Installation of this Django project is quite straightforward:

OS Dependencies
---------------

It is assumed you have:

+ python3 (Server runs on python 3.9)
+ python3-dev (python3.9-dev when using python3.9, relevant when running more then one python version on your computer)

Your host OS needs some packages, below is a list of debian packages:

+ libtiff5-dev
+ libjpeg62-turbo-dev
+ zlib1g-dev
+ libfreetype6-dev
+ liblcms2-dev
+ libwebp-dev
+ tcl8.6-dev
+ tk8.6-dev
+ libldap2-dev
+ libsasl2-dev
+ libssl-dev
+ gettext
+ libcairo2-dev
+ libpoppler-cpp-dev

Pip might throw errors while installing `mysqlclient` if you do not have a mysql-dev package. That package is not needed
for development, so you can (temporarily) comment out that dependency if you run into problems. (Or just install the
mysql dev package).

Preparing the source
--------------------

Clone the git repository

.. code:: shell

    git clone

Create a Python 3 virtual environment for this project and activate it:

.. code:: shell

    python3 -m venv DIR
    source venv/bin/activate

Install the requirements (in a virtualenv):

.. code:: shell

    pip install -r requirements.txt

Modify the settings file (`fetc/settings.py`) to your liking.

.. tip::
    It is recommended to keep the default database settings, as developing with a sqlite db is easier

Filling a database
------------------

Run the database migrations:

.. code:: shell

    python manage.py migrate

.. note::
    This will also create a sqlitedb file if it's missing


Setting up the fixtures
-----------------------
There are two ways to do this.

1. run the load_fixtures commando
=================================

.. code:: shell

    python manage.py load_fixtures

If this works you can skip step "load fixtures the old way" and go to create a superuser.

2. load fixtures the old way
============================

If for some reason the command load_fixtures does not work you can try the old way to load the fixtures

Load all fixtures using ``python manage.py loaddata``.

This command requires you to specify each fixture file, as it doesn't auto detect them.
For example:

.. code:: shell

    python manage.py loadddata relations.json

.. tip::
    You can find and install all fixture files with the following shell command (GNU tools only):

    .. code:: shell

        find $directory -type f -wholename "*fixtures/*.json" -print0 | xargs -0 python manage.py loaddata

:Create a superuser:

.. code:: shell

    python manage.py createsuperuser

Finishing touches
-----------------

Start the development server with ``python manage.py runserver``

By default, this starts the server at localhost, port 8000. You can specify a different location by supplying it
as an argument.

Example: ``python manage.py runserver localhost:8080`` or ``python manage.py runserver 8080``

Add additional users in the admin interface
===========================================

The application requires one user to be part of the 'secretary' group, otherwise the application will throw errors because it can't find one.
You can set this is the admin interface.

.. tip::
  You can find the admin interface at ``server:port/admin``. If you are using the default settings, this would be
  `http://localhost:8000/admin <http://localhost:8000/admin>`_.


.. tip::
   IT is advisable to create at least 3 user accounts:

   * A regular user, which you should use to create new studies
   * A user to use as a supervisor (some researchers need a supervisor)
   * A user to use as secretary


Setting up email
-----------------

In a non-production enviroment it is advised to change the email settings.
That can be done by creating an **debug_settings.py** file (if it doesn´t exist yet).
this file is en extension of settings.py where settings go that are to be included in .gitignore.
in debug_settings.py you need the following settings

.. note::
    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"

    EMAIL_FILE_PATH = "email/"

    EMAIL_FROM = "T.D.Mees@uu.nl"

    EMAIL_LOCAL_STAFF = "T.D.Mees@uu.nl"

Emails will now be send to a local directory instead of generating an error.

Setting up Translations
-----------------------
You only need one command to get the translations working.

.. code:: shell

    python manage.py compilemessages

.. tip::

    If you ever need to work with translations visit the i18n.rst file.

You are ready to roll!
----------------------

From now on, you can just use the ``runserver`` command to start the server. The server will also restart itself when
it detects changed source files, so you don't have to do this yourself (most of the time).