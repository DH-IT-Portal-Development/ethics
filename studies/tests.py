from __future__ import division

from proposals.tests import MiscProposalTestCase
from .models import Study
from .utils import STUDY_PROGRESS_START, STUDY_PROGRESS_TOTAL, get_study_progress



class ProgressTestCase(MiscProposalTestCase):
    def test_progress_single(self):
        self.p1.studies_number = 1
        self.p1.save()
        s1 = Study.objects.create(proposal=self.p1, order=1)
        self.assertEqual(STUDY_PROGRESS_START, get_study_progress(s1))

    def test_progress_double(self):
        self.p1.studies_number = 2
        self.p1.save()
        s1 = Study.objects.create(proposal=self.p1, order=1)
        s2 = Study.objects.create(proposal=self.p1, order=2)
        self.assertEqual(STUDY_PROGRESS_START, get_study_progress(s1))
        self.assertEqual(STUDY_PROGRESS_START + 1/2 * STUDY_PROGRESS_TOTAL, get_study_progress(s2))

    def test_progress_triple(self):
        self.p1.studies_number = 3
        self.p1.save()
        s1 = Study.objects.create(proposal=self.p1, order=1)
        s2 = Study.objects.create(proposal=self.p1, order=2)
        s3 = Study.objects.create(proposal=self.p1, order=3)
        self.assertEqual(int(STUDY_PROGRESS_START), get_study_progress(s1))
        self.assertEqual(int(STUDY_PROGRESS_START + 1/3 * STUDY_PROGRESS_TOTAL), get_study_progress(s2))
        self.assertEqual(int(STUDY_PROGRESS_START + 2/3 * STUDY_PROGRESS_TOTAL), get_study_progress(s3))
