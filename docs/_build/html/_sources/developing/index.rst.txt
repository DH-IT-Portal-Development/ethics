#######
General
#######

Structure
=========

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
