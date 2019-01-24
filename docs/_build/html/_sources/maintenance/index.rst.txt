############################
Maintenance & administration
############################

This section details some common maintenance and administration topics, like updating dependencies and user accounts.
It's written in the point of view of the current configuration, in contrast to the development section which is written
in a more neutral manner.

Periodic tasks
==============

Updating dependencies
---------------------

The dependencies used by the applications become outdated (and insecure) and should be updated semi-often.

Luckily, updating dependencies is very easy:

1. Run the following command:

   .. code:: shell

      pip-compile -U

   This should update the ``requirements.txt`` with the latest versions. If it doesn't, you can copy paste the terminal
   output into ``requirements.txt``

2. Test if everything is still working

3. Deploy the update on the servers

.. warning::

    You should use this guide for Django patch updates only. For feature updates (2.0 to 2.1 for example), see the next
    section.

Updating Django
---------------

Once in a while Django puts out a big update. At the moment we are using Django 1.11 LTS, which should be supported till
April 2020. However, one might decide to update to the latest feature update, or to the next LTS version. In that case,
you can use the following global steps as a guide.

1. Update Django's version constraints in ``requirements.in`` to next version in the series.

2. Go through Django's migration guide for that version and apply necessary changes

3. Test your changes

4. If everything works, go back to step 1 until you have reached the desired version.

5. Check if the application uses deprecated functions and try to migrate to the replacements (saves you or someone else
   a lot of time later).

Sporadic tasks / Frequently encountered problems
================================================

New user cannot log in
----------------------

Only users in the HUM-LDAP can log into the system. If a user reports they cannot log in, check if they are in the LDAP.

You can quickly do this with:

.. code:: shell

    python manage.py add_ldap_users SOLISID

If this errors, the user is not in the LDAP.
Otherwise, an account will be created/updated for that user. (Which confirms that they can in fact login).


Fixing proposals
----------------

Sometimes an update can cause some problems with draft proposals. To fix these, one might go into the database itself,
but this is hard. A better way is to do this through the Django shell.

Simply run the following command to start a shell:

.. code:: shell

    python manage.py shell

You can then import the model classes and modify them.

In the following simple example, we are going to create a Documents object for a study that is missing one

.. code:: python

    >> from proposals.models import Proposal
    >> from studies.models import Documents
    >> proposal = Proposal.object.get(pk=42)
    >> study = proposal.study_set.all()[0]
    >> documents = Documents()
    >> documents.proposal = proposal
    >> documents.study = study
    >> documents.save()

.. tip::
    Install bpython if it isn't installed yet. It will give you autocompletion in the shell, and more!