******************
Installation Steps
******************

.. todo:: better formatting

Installation of this Django project is quite straightforward:

- Clone the git repository

- Create a Python 3 virtual environment for this project:

  .. code:: shell

      python3 -m venv DIR

- Install the requirements (in a virtualenv):

  .. code:: shell

      pip install -r requirements.txt

- Modify the settings file (`etcl/settings.py`) to your liking.

  .. tip::
    It is recommended to keep the default database settings, as developing with a sqlite db is easier

- Run the database migrations:

  .. code:: shell

    python manage.py migrate

  .. note::
    This will also create a sqlitedb file if it's missing

- Load all fixtures using ``python manage.py loaddata``.

  This command requires you to specify each fixture file, as it doesn't auto detect them.
  For example:

  .. code:: shell

    python manage.py loadddata relations.json

  .. tip::
      You can find and install all fixture files with the following shell command (GNU tools only):

      .. code:: shell

          find $directory -type f -wholename "*fixtures/*.json" -print0 | xargs -0 python manage.py loaddata

- Create a superuser (``python manage.py createsuperuser``)

- Start the development server with ``python manage.py runserver``

  By default, this starts the server at localhost, port 8000. You can specify a different location by supplying it
  as an argument.

  Example: ``python manage.py runserver localhost:8080`` or ``python manage.py runserver 8080``

- Add additional users in the admin interface

  .. tip::
      You can find the admin interface at ``server:port/admin``. If you are using the default settings, this would be
      `http://localhost:8000/admin <http://localhost:8000/admin>`_.

  The application requires one user to be part of the 'secretary' group. You can set this is the admin interface.
  That same user should also be member of the 'committee' group.

  .. tip::
      You should create at least 2 user accounts, as you require a seperate account to act as a supervisor.

- You are ready to roll!

  From now on, you can just use the ``runserver`` command to start the server. The server will also restart itself when
  it detects changed source files, so you don't have to do this yourself (most of the time).