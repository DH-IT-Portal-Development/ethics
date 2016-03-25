from django.utils import timezone

from tasks.models import Task
from .utils import generate_ref_number


def copy_proposal(self, form):
    parent = form.cleaned_data['parent']
    title = form.cleaned_data['title']

    # Save relationships
    relation = parent.relation
    applicants = parent.applicants.all()
    copy_wmo = None
    copy_study = None
    if hasattr(parent, 'wmo'):
        copy_wmo = parent.wmo
    if hasattr(parent, 'study'):
        copy_study = parent.study
        copy_age_groups = parent.study.age_groups.all()
        copy_setting = parent.study.setting.all()
        copy_compensation = parent.study.compensation
        copy_recruitment = parent.study.recruitment.all()
        copy_surveys = parent.study.survey_set.all()
        copy_sessions = parent.study.session_set.all()
        copy_tasks = Task.objects.filter(session__study__proposal=parent)

    # Create copy and save the this new model, set it to not-submitted
    copy_proposal = parent
    copy_proposal.pk = None
    copy_proposal.reference_number = generate_ref_number(self.request.user)
    copy_proposal.title = title
    copy_proposal.created_by = self.request.user
    copy_proposal.date_created = timezone.now()
    copy_proposal.date_modified = timezone.now()
    copy_proposal.date_submitted_supervisor = None
    copy_proposal.date_reviewed_supervisor = None
    copy_proposal.date_submitted = None
    copy_proposal.date_reviewed = None
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants = applicants
    copy_proposal.parent = parent

    # Copy linked models
    if copy_wmo:
        copy_wmo.pk = copy_proposal.pk
        copy_wmo.save()

    if copy_study:
        copy_study.pk = copy_proposal.pk
        copy_study.age_groups = copy_age_groups
        copy_study.setting = copy_setting
        copy_study.compensation = copy_compensation
        copy_study.recruitment = copy_recruitment
        for survey in copy_surveys:
            copy_survey = survey
            copy_survey.pk = None
            copy_survey.study = copy_study
            copy_survey.save()
        copy_study.save()

    for session in copy_sessions:
        copy_session = session
        copy_session.pk = None
        copy_session.study = copy_study
        copy_session.save()
        copy_tasks_to_session(copy_session, copy_tasks)

    copy_proposal.save()

    return copy_proposal


def copy_tasks_to_session(session, tasks):
    for t in tasks:
        r = t.registrations.all()
        rk = t.registration_kinds.all()

        task = t
        task.pk = None
        task.session = session
        task.save()

        task.registrations = r
        task.registration_kinds = rk
        task.save()
