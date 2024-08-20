from .models import Study
from proposals.mixins import StepperContextMixin

class StudyMixin(
        StepperContextMixin,
):

    def get_proposal(self,):
        return self.get_object().proposal
