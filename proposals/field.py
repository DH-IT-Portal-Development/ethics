from django.forms import ModelChoiceField

from proposals.models import Proposal


class ParentChoiceModelField(ModelChoiceField):
    """
    Custom ModelChoiceField that uses a different function to determine
    what the labels of the options should be.

    This is done so we don't have to change the default __str__, just
    to make this form different.
    """
    def label_from_instance(self, obj: Proposal):
        last_modified = obj.date_modified.strftime("%b %d %Y %H:%M")
        if obj.is_practice():
            return '{} ({}) (Practice)'.format(obj.title, last_modified)
        return '{} ({})'.format(obj.title, last_modified)
