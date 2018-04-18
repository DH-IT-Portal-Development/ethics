from django import forms
from django.utils.datastructures import MultiValueDict

try:
    from django_auth_ldap.backend import LDAPBackend
except ImportError:
    # Define a dummy class if we can't import LDAPBackend for some reason
    class LDAPBackend(object):

        def populate_user(self, uid):
            pass


class SelectMultipleUser(forms.Select):
    """
    Custom widget to allow LDAP users to be entered through Select2.
    """
    allow_multiple_selected = True
    ldap = LDAPBackend()

    def value_from_datadict(self, data, files, name):
        # Get the right values
        if isinstance(data, MultiValueDict):
            values = data.getlist(name)
        else:
            values = data.get(name, None)

        for i, user in enumerate(values):
            # if the user id starts with ldap_, we need to add that user to our local cache
            if user.startswith('ldap_'):
                # Strip the ldap_ from the string
                uid = user[5:]

                # Import the user and get it's model object
                user_object = self.ldap.populate_user(uid)

                # Add the user as a valid option
                self.choices.append((user_object.pk, u'{}: {}'.format(user_object.username, user_object.get_full_name())))

                # Redefine the chosen option to the pk of the new user object
                values[i] = str(user_object.pk)

        return values
