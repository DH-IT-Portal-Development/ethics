****************
Deployment steps
****************

All steps (except step 6) are automated in a puppet module, but sometimes in a different order. You do not need to
actually do this yourself, but you should know what the module does. In case of a production deploy: make sure you check
that step 6 has been completed!

This guide assumes you are running on a Debian OS with Apache and MySQL.

1. Install prerequisites
========================
The following packages needs to be installed:

- Webserver with WSGI support. See ':doc:`webserver`'.
- Database. See ':doc:`database`'.
- Python 3:

    + python3
    + python3-dev
    + python3-tk
- Other packages:

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

2. Prepare Filesystem & Files
=============================

We're going to create a few folders to house our application. The current servers all have these folders as subfolders
of a ``data`` folder, next to the webroot and private folders.

All folders should be owned by the ``www-data`` user and group.

.. warning::
   None of the folders should be in a webroot, as this could expose sensitive information like passwords to the world.

   Webserver access to folder that need it is handled later in this guide.

Below is an overview of all folders we need, plus examples on how to get this folder

Source
------
This folder will hold the application source code. You should create this by cloning the source code from git. This way
you can update the code later by doing a simple git pull.

.. code:: bash

    $ git clone <repo> source
    $ chown www-data:www-data source

.. note::
    Currently, we use a bare clone of the repository on GitHub as the source repo on the production server. This is
    to make sure we do not accidentally push code to production.

    This would make the procedure on production:

    .. code:: bash

        $ git clone <repo> /path/to/repo --bare
        $ git clone /path/to/repo source
        $ chown www-data:www-data source

    When updating, you can either figure out how to update a bare repo, or you can delete the bare repo and re-clone.

Media
-----

This folder will hold all user uploaded/generated files.

.. code:: bash

    $ mkdir uploads
    $ chown www-data:www-data uploads

Static
------

This folder will be used for all static application files (css, images, etc).

.. code:: bash

    $ git clone <repo> static
    $ chown www-data:www-data static

Virtual environment
-------------------

This folder will hold the virtual environment that holds the application dependencies. It's best to create the env as
the www-data user.

.. code:: bash

    # su www-data
    $ python3 -m venv env

3. Python dependencies
======================

By this point you should be able to install your dependencies. You will also need to install `pip-tools`.

As your virtual environment should be owned by www-data, it's best to install these dependencies as www-data.

.. code:: bash

    # su www-data
    $ source env/bin/activate
    $ pip install pip-tools
    $ pip install -r source/requirements.txt

4. Configuration
================

Apache
------
*See* ':doc:`webserver`' *for more information.*

We need to hook up the application to Apache2. To do this, we need to create a configuration file in
``/etc/apache2/conf-enabled``.

An example config is provided in the ':doc:`webserver`' page. Use this to configure Apache2 to fit your situation.

.. warning::
    Do not restart Apache2 yet! This should be done at the end of the guide.

.. note::
    Technically it's better to create the config file in ``conf-available`` and then make a symlink to this file in
    ``conf-enabled``.

    However, the puppet script doesn't do this, as that requires more effort ¯\\_(ツ)_/¯.


Application
-----------
*See* ':doc:`configuration`' *for detailed information.*

.. note::
    The puppet module actually performs this step just after cloning the repository.

The ``settings.py`` file supplied with the source code is meant for development purposes. On a live server we want some
additional settings.

Please refer to the ':doc:`configuration`' page for detailed information on how the application should be configured.


5. Database
===========
*See* ':doc:`database`' *for more information.*

Create the database and database user as specified in the config file you just created.

After that, we need to install our application into it. For this, we use Django migrations:

.. code:: bash

    $ source env/bin/activate
    $ python source/manage.py migrate

Once this is done, we can put our data in. Either insert a dump from an existing database, or initialize an empty
database.

Filling a new database
----------------------
First we need to load all our fixtures. We can do this with the ``loaddata`` management command. You do need to specify
all the individual fixture files individually.

If you're on a POSIX system with GNU tools, you can use the following command to install all fixtures:

.. code:: bash

    find $directory -type f -wholename "*fixtures/*.json" -print0 | xargs -0 python manage.py loaddata

You also need to create a super user, using the ``createsuperuser`` management command:

.. code:: bash

    $ source env/bin/activate
    $ python source/manage.py createsuperuser

Use this superuser account to create a new account to serve as secretary. You can do this through the admin interface,
which can be found in ``/admin`` through your favourite browser. Make sure this user is part of the ``committee`` and
``secretary`` groups.

.. note::
    If using LDAP accounts, you can also add this user directly from the LDAP with the following management command:

    .. code:: bash

        $ source env/bin/activate
        $ python sourve/manage.py add_ldap_users <username>

    You still need to add this account to the proper groups through the admin interface, but this way your user can log
    in with his/her LDAP credentials.

6. Cron (production only)
=========================

.. warning::
    This step is **not** handled by the puppet module!

    Manual configuration is necessary.

Everyday at 7 AM, a cron task is scheduled to run a management command. This command sends out review reminders when
certain criteria are met.

To enable this, create a file in ``/etc/cron.d/`` to run the following command:

.. code::

    /path/to/env/bin/python /path/to/source/manage.py send_reminders

It's probably best to send the output to ``/dev/null``, as the sysadmin's probably panick when they get errors they
don't know.

An example of a full Cron definition (taken straight from the then-current production server):

.. code::

    0 7 * * * /hum/web/etcl.hum.uu.nl/data/etcl/env/bin/python /hum/web/etcl.hum.uu.nl/data/etcl/source/manage.py send_reminders >/dev/null 2>&1


7. Finishing up
===============

We're almost done, we only need to make our static files avaible, make sure we have the right translation file and
restart Apache.

Static files
------------

When Django is run in production mode, it doesn't serve static files like the development server does. This means that
we need to collect all static files in a folder that Apache2 can use to serve the files.

This can be achieved by running the ``collectstatic`` management command:

.. code:: bash

    $ source env/bin/activate
    $ python sourve/manage.py manage.py collectstatic --noinput

This will copy all static files to the folder specified in ``fetc/settings.py``.

Translation file
----------------

To make sure we use the right translation file, we recompile it from the source file.

This can be achieved by running the ``collectstatic`` management command:

.. code:: bash

    $ source env/bin/activate
    $ python sourve/manage.py manage.py compilemessages

Restart Apache
--------------

Now it's finally time to finish our deploy, by restarting apache. This can be done in your preferred way.

Some examples:

.. The echo statement is used to trick the syntax highlighter into displayed the following commands properly.

.. code:: bash

    $ echo 'Ignore me, I'm a workaround'
    # systemctl restart apache2
    # service apache2 restart
    # /usr/sbin/apache2ctl -k graceful
