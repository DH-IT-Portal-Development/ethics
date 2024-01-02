from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import AnonymousUser

from .models import Setting
from .utils import is_empty
from .validators import MaxWordsValidator


class BaseViewTestCase():
    """
    Inherit from this class to test the functioning of
    class-based views.
    """

    # This testcase supports only class-based views
    view_class = None

    # for example:
    # "/proposals/update/1/"
    # NOT a full URL including protocol and domain
    view_path = None

    allowed_users = []
    disallowed_users = [AnonymousUser]
    enforce_csrf = True

    def setUp(self):
        self.client = Client()
        self.view = self.view_class.as_view()
        self.factory = RequestFactory()
        super().setUp()

    def check_access(self, user):
        request = self.factory.get(
            self.get_view_path(),
        )
        request.user = user
        try:
            response = self.view(request, **self.get_view_args())
        except PermissionDenied:
            return False
        return response.status_code == 200

    def post(self, update_dict={}, user=AnonymousUser):
        """Generic function to test form submission"""
        post_data = {}
        post_data.update(update_dict)
        if self.enforce_csrf:
            csrf_token = self.fetch_csrf_token(
                user=user,
            )
            post_data["csrfmiddlewaretoken"] = csrf_token
        response = self.client.post(
            self.get_view_path(),
            data=post_data,
        )
        return response

    def fetch_csrf_token(self, user=None):
        if user:
            self.client.force_login(user)
        page = self.client.get(
            self.get_view_path(),
        )
        return page.context["csrf_token"]

    def get_view_path(self):
        return self.view_path


class ValidatorTest(TestCase):
    def test_max_words_validator(self):
        class Mock(models.Model):
            test = models.TextField(validators=[MaxWordsValidator(5)])

        try:
            m = Mock(test='Dit is een test')
            m.full_clean()
        except ValidationError:
            self.fail()

        with self.assertRaises(ValidationError):
            m = Mock(test='Dit is een test die faalt')
            m.full_clean()


class UtilsTest(TestCase):
    def test_is_empty(self):
        self.assertTrue(is_empty(None))
        self.assertFalse(is_empty(True))
        self.assertFalse(is_empty(False))

        self.assertTrue(is_empty([]))
        self.assertTrue(is_empty(Setting.objects.none()))
        self.assertFalse(is_empty(['']))

        self.assertTrue(is_empty(u''))
        self.assertTrue(is_empty(u'  '))
        self.assertFalse(is_empty(u' test '))
