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

Cloning the git repository, installing the requirements with pip and modifying the settings file should get you going.
Detailed instructions will be provided later on.

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

Language
--------

The main language of this web application is Dutch, as it's aimed towards the mostly avid Dutch-speaking researchers of Utrecht University.
However, since October 2016, there is a full English translation available, compiled by `Anna Asbury`_.
Translations in other languages are welcome, of course.

.. _Django: https://www.djangoproject.com/
.. _Ethical Committee Linguistics: https://etcl.wp.hum.uu.nl
.. _Utrecht University: https://www.uu.nl
.. _Anna Asbury: http://www.annaasbury.com/
