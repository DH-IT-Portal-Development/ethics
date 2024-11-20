from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _
from django.template import loader, Template, Context

import magic  # whoooooo
import pdftotext
from docx2txt import docx2txt

from main.models import Faculty
from fetc import constants

YES_NO = [(True, _("ja")), (False, _("nee"))]


class AvailableURL(object):
    def __init__(self, title, url=None, is_title=False, children=None, **kwargs):
        if not children:
            children = []

        self.title = title
        self.children = children
        self.url = url
        self.is_title = is_title
        self.kwargs = kwargs


def get_secretary():
    """
    Returns the Head secretary. We limit this to one user.
    """
    obj = (
        get_user_model()
        .objects.filter(groups__name=settings.GROUP_PRIMARY_SECRETARY)
        .first()
    )
    obj.email = settings.EMAIL_FROM
    return obj


def get_all_secretaries():
    """
    Return all users in the 'Secretary' group.
    """
    return get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY).all()


def is_secretary(user):
    """
    Check whether the current user is in the 'Secretary' group.
    """
    return Group.objects.get(name=settings.GROUP_SECRETARY) in user.groups.all()


def get_reviewers():
    return get_user_model().objects.filter(
        Q(groups__name=settings.GROUP_GENERAL_CHAMBER)
        | Q(groups__name=settings.GROUP_LINGUISTICS_CHAMBER)
    )


def get_reviewers_from_group(group):
    return get_user_model().objects.filter(groups__name=group)


def get_reviewers_from_groups(groups):
    return get_user_model().objects.filter(groups__name__in=groups).distinct()


def string_to_bool(s):
    if s == "None" or s is None:
        return False
    return s not in ["False", "false", "0", 0]


def get_users_as_list(users):
    """
    Retrieves all Users as a list.
    """
    return [
        (user.pk, "{}: {}".format(user.username, user.get_full_name()))
        for user in users
    ]


def is_empty(value):
    """
    Checks if value is filled out (!= None).
    For lists and strings, also check if the value is not empty.
    """
    result = False
    if value is None:
        result = True
    if hasattr(value, "__len__") and len(value) == 0:
        result = True
    if isinstance(value, str) and not value.strip():
        result = True
    return result


def get_static_file(file):
    return staticfiles_storage.url(file)


def get_document_contents(file: FieldFile) -> str:
    if file is None:
        return ""

    mime = magic.from_buffer(file.open(mode="rb").read(2048), mime=True)

    if mime == "application/pdf":
        with file.open(mode="rb") as f:
            pdf = pdftotext.PDF(f)
            return "\n\n".join(pdf)

    if mime == "application/octet-stream":
        # This _might_ not be a DocX, but as we only allow PDF and DocX we
        # know it should be fine
        with file.open(mode="rb") as f:
            return docx2txt.process(f)

    if (
        mime == "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document"
    ):
        with file.open(mode="rb") as f:
            return docx2txt.process(f)

    return f"No text found, or document not supported: ({mime})"


def is_member_of_faculty(user, faculty):
    return user.faculties.filter(internal_name=faculty).exists()


def is_member_of_humanities(user):
    return is_member_of_faculty(user, Faculty.InternalNames.HUMANITIES)


def can_view_archive(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    privileged_groups = [
        constants.GROUP_CHAIR,
        constants.GROUP_GENERAL_CHAMBER,
        constants.GROUP_LINGUISTICS_CHAMBER,
        constants.GROUP_SECRETARY,
        constants.GROUP_PRIMARY_SECRETARY,
    ]
    user_groups = user.groups.values_list(
        "name",
        flat=True,
    )
    for group in user_groups:
        if group in privileged_groups:
            return True
    # If our tests are inconclusive,
    # check for Humanities affiliation
    return is_member_of_humanities(user)


class renderable:

    def get_context_data(self, **kwargs):
        context = Context()
        context.update(kwargs)
        return context

    def render(self, extra_context={}, template_name=None):
        if not template_name:
            template_name = self.template_name
        context = self.get_context_data()
        template = loader.get_template(template_name)
        context.update(extra_context)
        return template.render(context.flatten())
