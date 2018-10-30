******
E-Mail
******

The application automatically sends out a few emails, so it might be handy to set up a local SMTP server using a tool
like `FakeSMTP`_ to receive these emails.

.. _FakeSMTP: http://nilhcem.com/FakeSMTP/index.html

As of the time of writing this page, not all email calls are fault-tolerant. You might get error's when Django cannot
connect to the SMTP server (for example, when it's not running).

Alternatively, you can use a different Django email backend like the console or file backends. For more information on
how to configure this, see the `related Django documentation`_.

.. _related Django documentation: https://docs.djangoproject.com/en/2.1/topics/email/#console-backend