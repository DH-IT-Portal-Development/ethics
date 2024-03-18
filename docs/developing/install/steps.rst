******************
Installation Steps
******************

Installation of this Django project is quite straightforward:

OS Dependencies
---------------

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

Load all fixtures using ``python manage.py loaddata``.

This command requires you to specify each fixture file, as it doesn't auto detect them.
For example:

.. code:: shell

    python manage.py loadddata relations.json

.. tip::
    You can find and install all fixture files with the following shell command (GNU tools only):

    .. code:: shell

        find $directory -type f -wholename "*fixtures/*.json" -print0 | xargs -0 python manage.py loaddata

Create a superuser

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

You are ready to roll!
----------------------

From now on, you can just use the ``runserver`` command to start the server. The server will also restart itself when
it detects changed source files, so you don't have to do this yourself (most of the time).