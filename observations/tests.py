from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Observation

""" TODO: tests below do not yet work
class ObservationTestCase(TestCase):
    def test_create(self):
        pk = 1
        response = self.client.get(reverse('observations:create', args=(pk,)))
        self.assertEqual(response.status_code, 200)

    def test_update(self):
        pk = 1
        response = self.client.get(reverse('observations:update', args=(pk,)))
        self.assertEqual(response.status_code, 200)
"""
