from django import forms
from django.utils.datastructures import MultiValueDict

try:
    from django_auth_ldap.backend import LDAPBackend
except ImportError:
    # Define a dummy class if we can't import LDAPBackend for some reason
    class LDAPBackend(object):
        def populate_user(self, uid):
            pass


class SelectUser(forms.Select):
    """
    Custom widget to allow a LDAP user to be entered through Select2.
    Used in combination with an ajax call to main:user_search
    """

    allow_multiple_selected = False
    ldap = LDAPBackend()

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)

        if value and value.startswith("ldap_"):
            # Strip the ldap_ from the string
            uid = value[5:]

            # Import the user and get it's model object
            user_object = self.ldap.populate_user(uid)

            # Add the user as a valid option
            self.choices.append(
                (
                    user_object.pk,
                    "{}: {}".format(user_object.username, user_object.get_full_name()),
                )
            )

            # Redefine the chosen option to the pk of the new user object
            value = str(user_object.pk)

        return value


class SelectMultipleUser(forms.Select):
    """
    Custom widget to allow multiple LDAP users to be entered through Select2.
    Used in combination with an ajax call to main:user_search
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
            if user.startswith("ldap_"):
                # Strip the ldap_ from the string
                uid = user[5:]

                # Import the user and get it's model object
                user_object = self.ldap.populate_user(uid)

                # Add the user as a valid option
                self.choices.append(
                    (
                        user_object.pk,
                        "{}: {}".format(
                            user_object.username, user_object.get_full_name()
                        ),
                    )
                )

                # Redefine the chosen option to the pk of the new user object
                values[i] = str(user_object.pk)

        return values
