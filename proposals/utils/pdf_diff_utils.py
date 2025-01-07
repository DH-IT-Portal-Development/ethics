from datetime import date, datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.urls import reverse

from main.templatetags.fetc_filters import create_unordered_html_list


class BaseSection:
    """This is the main class, from which sections are constructed.
    It receives one object, such as a proposal or sub-objects of proposals.
    The most important methods are render and make_rows. Make rows makes use of get_row_field,
    which gets overwritten for specific sections, if logic is involved.
    For certain sections, there can be a sub-title, such as for studies or other cases.
    These are produced in the get_sub_title method and require a specific string, based on
    the type of sub-title required. The options are:
    - 'study'
    - 'session'
    - 'task'
    -'task_overview'
    These arguments are passed in overwritten __init__() methods, when applicable.
    """

    section_title = None
    row_fields = None

    def __init__(self, obj):
        self.obj = obj
        self.sub_title = None

    def make_rows(self):
        rows = [self.make_row_for_field(field) for field in self.get_row_fields()]
        return rows

    def make_row_for_field(self, field):
        if field in self.get_row_fields():
            return Row(self.obj, field)
        else:
            return None

    def get_row_fields(self):
        return self.row_fields

    def render(self, context):
        context = context.flatten()
        template = get_template("proposals/table_with_header.html")
        if self.sub_title is not None:
            context.update(
                {
                    "sub_title": self.sub_title,
                }
            )
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.make_rows(),
            }
        )
        return template.render(context)

    def get_sub_title(self, obj, sub_title_type):
        return SubTitle(obj, sub_title_type).sub_title


class DiffSection:
    """For the diff page, sections are constructed by comparing two section objects.
    for instance:
          GeneralSection(old_proposal), GeneralSection(new_proposal)

    It mostly uses the make_rows methods, but also some other class variables from these objects.
    If a section is missing from a revision or an original proposal, this will be reperesented by
    None, and a warning and some formatting info get passed to the template as well.

    Some parts of this were written with the idea of allowing more than two objects to be compared,
    however, I did not end up pursuing this idea until the end."""

    def __init__(self, old_section, new_section):
        self.old_section = old_section
        self.new_section = new_section
        if self.old_section is None:
            self.warning = _(
                "Dit onderdeel is nieuw in de revisie en bestond niet in de originele aanvraag."
            )
            self.missing_object = "old"
            self.sub_title = self.new_section.sub_title
            self.section_title = self.new_section.section_title
        elif self.new_section is None:
            self.warning = _(
                "Dit onderdeel bestond in de originele aanvraag, maar niet meer in de revisie."
            )
            self.missing_object = "new"
            self.sub_title = self.old_section.sub_title
            self.section_title = self.old_section.section_title
        else:
            self.warning = None
            self.missing_object = None
            self.sub_title = self.old_section.sub_title
            self.section_title = self.old_section.section_title
        self.rows = self.make_diff_rows()

    def make_diff_rows(self):
        """This function generates rows for diff instances."""

        if self.missing_object is not None:
            # If there is a missing object, the template can just use the make_rows function
            # of the object that is not missing.
            if self.missing_object == "old":
                rows = self.new_section.make_rows()
            else:
                rows = self.old_section.make_rows()
            return rows
        else:
            all_fields = self.old_section.row_fields

            rows = []

            old_rows = self.old_section.make_rows()
            new_rows = self.new_section.make_rows()

            old_section_dict = {row.field: row for row in old_rows}
            new_section_dict = {row.field: row for row in new_rows}

            for field in all_fields:
                # If a field does not appear in either section, no row will be created.
                if field in old_section_dict and field in new_section_dict:
                    rows.append(
                        {
                            "verbose_name": old_section_dict[field].verbose_name,
                            "old_value": old_section_dict[field].value,
                            "new_value": new_section_dict[field].value,
                        }
                    )
                elif field in old_section_dict and not field in new_section_dict:
                    rows.append(
                        {
                            "verbose_name": old_section_dict[field].verbose_name,
                            "old_value": old_section_dict[field].value,
                            "new_value": "",
                        }
                    )
                elif field in new_section_dict and not field in old_section_dict:
                    rows.append(
                        {
                            "verbose_name": new_section_dict[field].verbose_name,
                            "old_value": "",
                            "new_value": new_section_dict[field].value,
                        }
                    )

            return rows

    def render(self, context):
        context = context.flatten()
        template = get_template("proposals/table_with_header_diff.html")

        if self.warning is not None:
            context.update(
                {
                    "warning": self.warning,
                    "missing_object": self.missing_object,
                }
            )
        if self.sub_title is not None:
            context.update(
                {
                    "sub_title": self.sub_title,
                }
            )
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.rows,
            }
        )
        return template.render(context)


class Row:
    """This class creates rows for one objects, and gets initated
    in the make_rows method of Section classes. The classmethods of Rowclass
    are called in the templates of the render method of the PDF class, as well as in
    the make_diff_rows() method of the DiffSection"""

    verbose_name_diff_field_dict = {
        "get_metc_display": "metc",
        "get_is_medical_display": "is_medical",
    }

    def __init__(self, obj, field, proposal=None):
        self.obj = obj
        self.field = field
        self.proposal = proposal

    def value(self):
        return RowValue(self.obj, self.field, self.proposal).get_field_value()

    def verbose_name(self):
        if self.field in self.verbose_name_diff_field_dict:
            verbose_name_field = self.verbose_name_diff_field_dict[self.field]
            verbose_name = self.get_verbose_name(verbose_name_field)
        else:
            verbose_name = self.get_verbose_name(self.field)
        return verbose_name

    def get_verbose_name(self, field):
        if field != "tasks_duration":
            return mark_safe(self.obj._meta.get_field(field).verbose_name)
        else:
            return mark_safe(
                self.obj._meta.get_field(field).verbose_name % self.obj.net_duration()
            )


class KindRow(Row):
    """
    Create a row for a very specific edge case, namely attachment.kind.
    It needs to use attachment's verbose name, but get the value from slot.
    """

    def __init__(self, slot, attachment, field):
        self.slot = slot
        self.obj = attachment
        self.field = field

    def value(self):
        return self.slot.kind.name


class UploadDateRow:
    """
    Another very specific row case for attachments. This one just needed to be
    fully custom and hardly related to the normal Row ...
    """

    def __init__(self, attachment, field):
        self.field = field
        self.attachment = attachment

    def value(self):
        return datetime.date(self.attachment.upload.file_instance.modified_on)

    def verbose_name(self):
        return _("Uploaddatum")


class RowValue:
    """The RowValue class manages the values of fields and correctly retrieves and/or formats
    the right values per field. This class get initiated in the value method
    of the Row class. It returns mostly strings, but sometimes some html as well."""

    def __init__(self, obj, field, proposal=None):
        self.obj = obj
        self.field = field
        self.proposal = proposal

    def get_field_value(self):
        from ..models import Relation
        from studies.models import Study, Compensation

        value = getattr(self.obj, self.field)

        User = get_user_model()

        if value in ("Y", "N", "?"):
            return self.yes_no_doubt(value)
        elif isinstance(value, bool):
            return _("ja") if value else _("nee")
        elif isinstance(value, int) and self.field == "legal_basis":
            return Study.LegalBases(value).label
        elif isinstance(value, (str, int, date)):
            return value
        elif value is None:
            return _("Onbekend")
        elif isinstance(value, User):
            return self.handle_user(value)
        elif isinstance(value, Relation) or isinstance(value, Compensation):
            return value.description
        if value.__class__.__name__ == "FileWrapper":
            return self.handle_attachment(value)
        elif value.__class__.__name__ == "ManyRelatedManager":
            if value.all().model == User:
                return self.get_applicants_names(value)
            else:
                return self.get_object_list(value)
        elif value.__class__.__name__ == "FieldFile":
            return self.handle_field_file(value)
        elif callable(value):
            return value()

    def handle_user(self, user):
        return user.get_full_name()

    def get_applicants_names(self, applicants):
        applicant_names = [applicant.get_full_name() for applicant in applicants.all()]
        return create_unordered_html_list(applicant_names)

    def get_object_list(self, object):
        list_of_objects = [obj for obj in object.all()]
        return create_unordered_html_list(list_of_objects)

    def handle_field_file(self, field_file):
        """This is for legacy attachments"""
        if field_file:
            output = format_html(
                '<a href="{}">{}</a>',
                f"{settings.BASE_URL}{field_file.url}",
                _("Download"),
            )
        else:
            output = _("Niet aangeleverd")

        return output

    def handle_attachment(self, filewrapper):

        if filewrapper:
            output = format_html(
                '<a href="{}">{}</a>',
                settings.BASE_URL
                + reverse(
                    "proposals:download_attachment",
                    kwargs={
                        "proposal_pk": self.proposal.pk,
                        "attachment_pk": self.obj.pk,
                    },
                ),
                _("Download"),
            )
        else:
            output = _("Niet aangeleverd")

        return output

    def yes_no_doubt(self, value):
        from main.models import YesNoDoubt

        return YesNoDoubt(value).label


class SubTitle:
    """This class can return a sub title to the base section class,
    according to the argument with which it is initiated. This argument gets passed
    in overwritten __init__ methods of for instance, the StudySection class."""

    def __init__(self, object, sub_title_type):
        if sub_title_type == "study":
            self.sub_title = self.get_study_title(object)
        elif sub_title_type == "session":
            self.sub_title = self.get_session_title(object)
        elif sub_title_type == "task":
            self.sub_title = self.get_task_title(object)
        elif sub_title_type == "task_overview":
            self.sub_title = _("Overzicht van het takenonderzoek")
        else:
            self.sub_title = None

    def get_study_title(self, study):
        from studies.models import Study

        if not isinstance(study, Study):
            study = study.study
        if study.proposal.studies_number > 1:
            if study.name:
                study_title = format_html(
                    "{}{} <em>{} </em>",
                    _("Traject "),
                    study.order,
                    study.name,
                )
            else:
                study_title = format_html(
                    "{}{}",
                    _("Traject"),
                    {study.order},
                )
        else:
            study_title = None
        return study_title

    def get_session_title(self, session):
        if session is None:
            return ""
        else:
            order = session.order
            study_order = session.study.order
            study_name = session.study.name
            studies_number = session.study.proposal.studies_number
            sessions_number = session.study.sessions_number

            if studies_number > 1 and sessions_number > 1:
                session_title = format_html(
                    "{}{} <em>{} </em> {}{}",
                    _("Traject "),
                    study_order,
                    study_name,
                    _("sessie "),
                    order,
                )
            elif studies_number > 1:
                session_title = format_html(
                    "{}{} <em>{} </em>",
                    _("Traject "),
                    study_order,
                    study_name,
                )
            elif sessions_number >= 1:
                session_title = format_html(
                    "{}{}",
                    _("Sessie "),
                    order,
                )
            return session_title

    def get_task_title(self, task):
        if task is None:
            return ""
        else:
            order = task.order
            session_order = task.session.order
            study_order = task.session.study.order
            study_name = task.session.study.name
            studies_number = task.session.study.proposal.studies_number
            if studies_number > 1:
                task_title = format_html(
                    "{}{} <em>{} </em>, {}{}{}{}",
                    _("Traject "),
                    study_order,
                    study_name,
                    _("sessie "),
                    session_order,
                    _(", taak "),
                    order,
                )
            else:
                task_title = format_html(
                    "{}{}{}{}",
                    _("Sessie "),
                    session_order,
                    _(", taak "),
                    order,
                )
            return task_title


class PageBreakMixin(BaseSection):
    """A Mixin for adding page break formatting to a section."""

    def render(self, context):
        context.update(
            {
                "page_break": True,
            }
        )
        return super().render(context)


def get_extra_documents(obj):
    """A function to retrieve all extra documents for a specific proposal."""
    from studies.models import Documents

    extra_documents = []

    for document in Documents.objects.filter(proposal=obj, study__isnull=True):
        extra_documents.append(document)

    return extra_documents


def multi_sections(section_type, objects, num=None):
    """A function that creates a list of sections of a specified type, from a list of
    objects, where it is possible for an object, such as a study, to be missing."""

    if num is None:
        return [section_type(obj) if obj is not None else None for obj in objects]
    else:
        return [section_type(obj, num) if obj is not None else None for obj in objects]


def get_all_related(objects, related_name):
    """Helper function for retrieving related objects"""

    return [
        getattr(obj, related_name, None) if obj is not None else None for obj in objects
    ]


def get_all_sessions(studies):
    """
    Receives a list of study objects and gets sessions for the study
    """
    return [study.get_sessions() if study is not None else None for study in studies]


def get_all_related_set(objects, related_name):
    """Helper function for retrieving a set of related objects."""

    return [
        getattr(obj, related_name, None).all() if obj is not None else None
        for obj in objects
    ]
