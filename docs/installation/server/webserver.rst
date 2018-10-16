*********
Webserver
*********

As with most Python webapps, communication with the webserver is done through the Web Server Gateway Interface. For more
information on the WSGI spec, see `PEP333`_ and `PEP3333`_.

.. _PEP333: https://www.python.org/dev/peps/pep-333/
.. _PEP3333: https://www.python.org/dev/peps/pep-3333/

A WSGI application is supplied in the :mod:`etcl.wsgi` module. You can point your webserver to this file, providing that
your webserver speaks WSGI.

Apache
======
`Django documentation`_

.. _Django documentation: https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/modwsgi/


For deployment on our own servers we use Apache2's ``mod_wsgi`` in daemon mode. It's important that you install the
python 3 version. Most linux distro's supply the Python2 version by default, but offer the Python 3 version through a
different package. For example, Debian uses the ``libapache2-mod-wsgi-py3`` package.

Virtual environment
-------------------

Python virtual environments and ``mod_wsgi`` do not mix together easily. This is because ``mod_wsgi`` actually contains
an embedded version of the CPython interpreter.

.. note::
   The embedded interpreter should not be confused with ``mod_wsgi``'s embedded mode. Both embedded mod and daemon mode
   use the embedded interpreter. Embedded mode only embeds the interpreter in the main Apache2 process instead of
   creating a seperate process.

This has a few implications, most importantly the fact that virtual environment needs to be created by the same version
of Python that ``mod_wsgi`` was build with. Luckily, most (if not all) Linux distributions build their ``mod_wsgi``
package with the Python binary they ship withthe distribution. So as long as you use the correct Python version, you
shouldn't have any problems.

As Apache will not use the binary in the virtual environment, you also need to instruct Apache's Python where to find
it's python libraries. This can be done by specifying the ``python-path`` variable in the Apache ``WSGIDaemonProcess``
setting.

.. attention::
   You need to specify both the site-packages folder of your virtualenv and the folder containing your source files. You
   need to seperate both folders with a ``:``.

   For example:

   .. code:: apacheconf

       WSGIDaemonProcess etcl python-path=/path/to/app_src:/path/to/env/lib/python{version}/site-packages lang='en_US.UTF-8' locale='en_US.UTF-8'

   The lang and locale parameters are optional, but encouraged.

vHost config
------------

In most cases you'd configure WSGI on a vHost level. In our case, we actually configure it on a Apache level trough a
config file in the ``/etc/apache2/conf-enabled``. This means it will apply to **all** vHosts on the server.

In the current situation, this isn't a problem as we only have the one vHost. (Ignoring the http to https redirect).
If for some reason a new set of vHost's need to be added, the WSGI config should be moved into a vHost config.

The main benefit of configuring WSGI this way is the fact that we that we can change the config ourselves. Any change
to the vHost file needs to be done in the main Puppet config for the VM.

Example config
--------------
Based upon code provided in the `Django documentation`_

.. code:: apacheconf

    # This disables embedded mode, which removes a lot of Apache overhead
    WSGIRestrictEmbedded On

    WSGIScriptAlias / /path/to/wsgi/wsgi.py
    WSGIDaemonProcess etcl python-path= <See above>
    WSGIProcessGroup etcl

    Alias /static/ /path/to/static_folder/
    Alias /media/ /path/to/media_folder/

    <Directory /path/to/static_folder/>
        Require all granted
    </Directory>

    <Directory /path/to/media_folder/>
        Require all granted
    </Directory>

    <Directory /path/to/source_folder/>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
