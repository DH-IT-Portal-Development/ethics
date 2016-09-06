from django.core.management.base import BaseCommand, CommandError
from django_auth_ldap.backend import LDAPBackend


class Command(BaseCommand):
    help = 'Adds users from the LDAP backend'

    def add_arguments(self, parser):
        parser.add_argument('usernames', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['usernames']:
            user = LDAPBackend().populate_user(username)
            if user is None:
                raise CommandError('No user named {}'.format(username))
