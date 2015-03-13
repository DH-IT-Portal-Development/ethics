"""
Django settings for ethics project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j8dwfg6kvg=fnfs33s0x(t&0pfe)p9$3dm943)6hvurj6@=+4j'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'bootstrap3',
    'proposals',
    #'reviews',
    #'meetings',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ethics.urls'

WSGI_APPLICATION = 'ethics.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', 
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
    ,
    'mysql': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ethics',
        'USER': 'root',
        'PASSWORD': 'root++',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Authentication (via LDAP)

LOGIN_REDIRECT_URL = '/proposals/'

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = 'ldap://ldap.forumsys.com'
AUTH_LDAP_BIND_DN = 'cn=read-only-admin,dc=example,dc=com'
AUTH_LDAP_BIND_PASSWORD = 'password'
AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,dc=example,dc=com'
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'uid', 
    'last_name': 'sn'
}
AUTH_LDAP_ALWAYS_UPDATE_USER = False

from django_auth_ldap.backend import populate_user 

def make_staff(sender, user, **kwargs): 
    user.is_staff = True 
    user.is_superuser = True 

populate_user.connect(make_staff) 

#AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
#AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=scientists,dc=example,dc=com', ldap.SCOPE_SUBTREE, '(objectClass=groupOfUniqueNames)')
#AUTH_LDAP_USER_FLAGS_BY_GROUP = {
#    'is_active': 'cn=scientists,dc=example,dc=com',
#    'is_staff': 'cn=scientists,dc=example,dc=com',
#    'is_superuser': 'cn=scientists,dc=example,dc=com',
#}

#import logging

#logger = logging.getLogger('django_auth_ldap')
#logger.addHandler(logging.StreamHandler())
#logger.setLevel(logging.DEBUG)

# File handling
MEDIA_ROOT = 'C:\Users\Martijn\Documents\Werk\Universiteit Utrecht\ethics\media'
