from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from menu import Menu, MenuItem

Menu.add_item("home", MenuItem(_("Startpagina"), reverse("main:home"), exact_url=True))

Menu.add_item(
    "footer",
    MenuItem(
        _("Log in"), settings.LOGIN_URL, check=lambda x: not x.user.is_authenticated
    ),
)

Menu.add_item(
    "footer",
    MenuItem(_("Log uit"), reverse("logout"), check=lambda x: x.user.is_authenticated),
)
