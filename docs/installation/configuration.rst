*************************
Application configuration
*************************

The git repository contains a ``settings.py`` file suitable for development. Some tweaks are required for a
production/acceptation server.

settings.py
===========

General
-------

Logging
-------

Database
--------

Static/Media files
------------------

Email
-----

ldap_settings.py
================
By default, the project doesn't have the required files to use LDAP based authentication. To enable this, you need to
create a file called ``ldap_settings.py`` in the ``etcl`` folder using the following template:

.. code-block:: python

    import logging

    AUTHENTICATION_BACKENDS = (
        'django_auth_ldap.backend.LDAPBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

    # Authentication (via LDAP)
    AUTH_LDAP_SERVER_URI = ''
    AUTH_LDAP_START_TLS = True
    AUTH_LDAP_BIND_DN = ''
    AUTH_LDAP_BIND_PASSWORD = ''
    AUTH_LDAP_USER_DN_TEMPLATE = ''
    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': '',
        'last_name': '',
        'email': ''
    }
    AUTH_LDAP_ALWAYS_UPDATE_USER = True

We will now explain what each of these contants actually do. Please note that full documentation about Django LDAP auth
can be found `here`_.

.. _here: https://django-auth-ldap.readthedocs.io/

AUTHENTICATION_BACKENDS
-----------------------
You don't have to change anything here. It only overrides the default value by adding the ``LDAPBackend`` authentication
backend.

The ``ModelBackend`` is still needed as it's used to assign users to groups internally. We cannot use the LDAP for this,
as the LDAP does not contain the necessary information.

.. warning::

    Always create user accounts from the LDAP if you can, as this is connected to the university's IAM system. Local
    accounts are **evil** and should only be used in emergencies!

AUTH_LDAP_SERVER_URI
--------------------
This is the location of the LDAP you want to use. Please include the ``ldap://``.

For the ETCL we use an ICT&Media LDAP: ``ldap://ldap.hum.uu.nl``

.. note::

    While it might seem logical to use the ``ldaps://`` protocol, it's not recommended to do so.

    Secure connections can be enforced with the ``AUTH_LDAP_START_TLS`` setting.

AUTH_LDAP_START_TLS
-------------------
If set to true, this will enforce a secure connection to the LDAP server. While in theory the connections are internal
only, it doesn't hurt (that much) to use secure connections.

AUTH_LDAP_BIND_DN
-----------------
If your LDAP server doesn't allow for anonymous login, you need to specify a bind DN here. Otherwise you can leave it
empty.

You can request a bind DN from ICT&Media if needed. (Or you could just get one from one of the existing servers).

AUTH_LDAP_BIND_PASSWORD
-----------------------
If you have supplied a bind DN in ``AUTH_LDAP_BIND_DN``, you have to supply it's password here.

AUTH_LDAP_USER_DN_TEMPLATE
--------------------------
When logging in, Django will query the LDAP with an exact DN for that user. To create this DN, Django will use this
constant. Use ``%(user)s`` where the user's username should be in the DN.

For example: ``uid=%(user)s,ou=People,dc=uu,dc=nl``

.. note::

    You can also configure the LDAP auth to use an LDAP search instead of a direct match. More information can be found
    in the `corresponding documentation`_.

.. _corresponding documentation: https://django-auth-ldap.readthedocs.io/en/latest/authentication.html#search-bind

AUTH_LDAP_USER_ATTR_MAP
-----------------------
This constant should contain a dictorary that maps LDAP fields to  Django's auth model fields.

For example (when using ICT&Media's LDAP):

.. code-block:: python

    AUTH_LDAP_USER_ATTR_MAP = {
        'first_name': 'givenName',
        'last_name': 'humAchternaam',
        'email': 'mail'
    }

.. warning::

    If you enter an invalid LDAP field, no error will be given and an empty string will be supplied to the auth model.

    Please double check all values.

AUTH_LDAP_ALWAYS_UPDATE_USER
----------------------------
If set to True, this will update the user model in the database with the values in the LDAP on every login.

Passwords are always checked against the LDAP regardless of this setting.