from .utils import generate_ref_number


def copy_proposal(self, form):
    parent = form.cleaned_data['parent']
    relation = parent.relation
    applicants = parent.applicants.all()
    copy_wmo = None
    copy_study = None
    if hasattr(self, 'wmo'):
        copy_wmo = parent.wmo
    if hasattr(self, 'study'):
        copy_study = parent.study
    #copy_sessions = parent.session_set.all()

    # Create copy and save the this new model
    copy_proposal = parent
    copy_proposal.pk = None
    copy_proposal.reference_number = generate_ref_number(self.request.user)
    copy_proposal.title = 'Kopie van %s' % copy_proposal.title
    copy_proposal.created_by = self.request.user
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants = applicants
    copy_proposal.parent = parent

    # Copy linked models TODO: finish this
    if copy_wmo:
        copy_wmo.pk = copy_proposal.pk
        copy_wmo.save()

    if copy_study:
        copy_study.pk = copy_proposal.pk
        copy_study.save()

    #copy_proposal.session_set = copy_sessions

    # TODO: copy tasks

    return copy_proposal
