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
        return Study.objects.get(pk=self.kwargs["pk"])

    def get_proposal(
        self,
    ):
        return self.get_study().proposal
