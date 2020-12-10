from typing import List

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

from main.templatetags.fetc_filters import in_general_chamber, \
    in_linguistics_chamber, is_secretary


def create_committee_menu(commitee: str) -> List[MenuItem]:
    return [
        MenuItem(
            _("Mijn openstaande besluiten"),
            reverse("reviews:my_open", args=[commitee]),
        ),
        MenuItem(
            _("Al mijn besluiten"),
            reverse("reviews:my_archive", args=[commitee]),
        ),
        MenuItem(
            _("Alle openstaande besluiten commissieleden"),
            reverse("reviews:open", args=[commitee]),
            check=lambda x: is_secretary(x.user),
        ),
        MenuItem(
            _("Alle openstaande besluiten eindverantwoordelijken"),
            reverse("reviews:open_supervisors", args=[commitee]),
            check=lambda x: is_secretary(x.user),
        ),
        MenuItem(
            _("Nog af te handelen studies"),
            reverse("reviews:to_conclude", args=[commitee]),
            check=lambda x: is_secretary(x.user),
        ),
        MenuItem(
            _("Alle ingezonden studies"),
            reverse("reviews:archive", args=[commitee]),
            check=lambda x: is_secretary(x.user),
        ),
    ]


Menu.add_item("main", MenuItem(
    _("Algemene Kamer"),
    "#",
    children=create_committee_menu('AK'),
    check=lambda x: in_general_chamber(x.user)
))

Menu.add_item("main", MenuItem(
    _("Linguïstiek Kamer"),
    "#",
    children=create_committee_menu('LK'),
    check=lambda x: in_linguistics_chamber(x.user)
))
