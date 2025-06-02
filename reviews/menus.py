from typing import List

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

from main.templatetags.fetc_filters import (
    in_general_chamber,
    in_linguistics_chamber,
    is_chair_or_secretary,
    is_po_chair_or_secretary,
)

from main.utils import get_user


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
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Alle openstaande besluiten eindverantwoordelijken"),
            reverse("reviews:open_supervisors", args=[commitee]),
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Nog af te handelen aanvragen"),
            reverse("reviews:to_conclude", args=[commitee]),
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Aanvragen in revisie"),
            reverse("reviews:in_revision", args=[commitee]),
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Alle lopende aanvragen"),
            reverse("reviews:all_open", args=[commitee]),
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Alle ingezonden aanvragen"),
            reverse("reviews:archive", args=[commitee]),
            check=lambda x: is_po_chair_or_secretary(get_user(x)),
        ),
        MenuItem(
            _("Overzicht werkverdeling commissieleden"),
            reverse("reviews:workload", args=[commitee]),
            check=lambda x: is_chair_or_secretary(get_user(x)),
        ),
    ]


Menu.add_item(
    "main",
    MenuItem(
        _("Algemene Kamer"),
        "#",
        children=create_committee_menu("AK"),
        check=lambda x: in_general_chamber(get_user(x)),
    ),
)

Menu.add_item(
    "main",
    MenuItem(
        _("Linguïstiek Kamer"),
        "#",
        children=create_committee_menu("LK"),
        check=lambda x: in_linguistics_chamber(get_user(x)),
    ),
)
