from django.http import Http404

from .models import Study
from proposals.mixins import StepperContextMixin


class StudyMixin(
    StepperContextMixin,
):

    def get_proposal(
        self,
    ):
        return self.get_object().proposal


class StudyFromURLMixin:

    def get_study(self):
        """Retrieves the Study from the pk kwarg"""
        try:
            return Study.objects.get(pk=self.kwargs["pk"])
        except Study.DoesNotExist:
            raise Http404

    def get_proposal(
        self,
    ):
        return self.get_study().proposal
