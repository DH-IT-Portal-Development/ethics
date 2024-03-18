from django.urls import reverse
from django.test import TestCase


class ObservationTestCase(TestCase):
    def test_create(self):
        pk = 1
        response = self.client.get(reverse("observations:create", args=(pk,)))
        self.assertEqual(response.status_code, 302)

    def test_update(self):
        pk = 1
        response = self.client.get(reverse("observations:update", args=(pk,)))
        self.assertEqual(response.status_code, 302)
