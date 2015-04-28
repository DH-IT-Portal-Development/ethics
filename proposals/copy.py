def copy_proposal(self, form):
    parent = form.cleaned_data['parent']
    relation = parent.relation
    applicants = parent.applicants.all()
    copy_wmo = parent.wmo

    # Create copy and save the this new model
    copy_proposal = parent
    copy_proposal.pk = None
    copy_proposal.title = 'Kopie van %s' % copy_proposal.title
    copy_proposal.created_by = self.request.user
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants = applicants
    copy_proposal.parent = parent

    # Copy linked models TODO: finish this
    copy_wmo.pk = copy_proposal.pk
    copy_wmo.save()

    return copy_proposal
