"""Copy this file to saml_settings.py if you want to use local SAML

You'll also need some certs, this code assumes they are located in a 'certs'
dir at the project-root.
"""
import os

from cdh.federated_auth.saml.settings import *
_BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SAML_DEFAULT_BINDING = saml2.BINDING_HTTP_POST

SAML_CONFIG = create_saml_config(
    base_url='http://localhost:8000/',
    name='FEtC-H Portal',
    key_file=os.path.join(_BASE_DIR, 'certs/private.key'),
    cert_file=os.path.join(_BASE_DIR, 'certs/public.cert'),
    idp_metadata='http://localhost:7000/saml/idp/metadata/',
    allow_unsolicited=True,
    contact_given_name='Humanities IT Portal Development',
    contact_email='portaldev.gw@uu.nl',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'djangosaml2.backends.Saml2Backend',
)