from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

from main.utils import is_secretary

new_proposal_menu = (
    MenuItem(
        _("Nieuwe studie starten"),
        reverse("proposals:start"),
    ),
    MenuItem(
        _("Nieuwe studie starten op basis van een kopie van een oude studie"),
        reverse("proposals:copy"),
    ),
    MenuItem(
        _("Nieuwe studie starten voor (al dan niet goedgekeurde) subsidieaanvragen"),
        reverse("proposals:start_pre"),
    ),
    MenuItem(
        _("Nieuwe studie starten (die al goedgekeurd is door een andere "
          "ethische toetsingscomissie)"),
        reverse("proposals:start_pre_approved"),
    ),
    MenuItem(
        _("Nieuwe oefenstudie starten"),
        reverse("proposals:start_practice"),
    ),
    MenuItem(
        _("Maak een revisie van een bestaande studie"),
        reverse("proposals:copy_revision"),
    ),
    MenuItem(
        _("Maak een amendement van een al goedgekeurde studie"),
        reverse("proposals:copy_amendment"),
    ),
)

Menu.add_item(
    "main",
    MenuItem(
        _("Nieuwe studie"),
        "#",
        slug='new-studies',  # needed for sub-menu!
        children=new_proposal_menu,
        check=lambda x: x.user.is_authenticated,
    )
)

my_proposals_menu = (
    MenuItem(
        _("Al mijn studies"),
        reverse("proposals:my_archive"),
    ),
    MenuItem(
        _("Mijn conceptstudies"),
        reverse("proposals:my_concepts"),
    ),
    MenuItem(
        _("Mijn oefenstudies"),
        reverse("proposals:my_practice"),
    ),
    MenuItem(
        _("Mijn ingediende studies"),
        reverse("proposals:my_submitted"),
    ),
    MenuItem(
        _("Mijn afgehandelde studies"),
        reverse("proposals:my_completed"),
    ),
    MenuItem(
        _("Mijn studies als eindverantwoordelijke"),
        reverse("proposals:my_supervised"),
    ),
)

Menu.add_item(
    "main",
    MenuItem(
        _("Mijn studies"),
        reverse("proposals:my_archive"),
        slug='my-studies',  # needed for sub-menu!
        children=my_proposals_menu,
        check=lambda x: x.user.is_authenticated,
    )
)

archive_menu = (
    MenuItem(
        _("Alle studies bekijken van de Algemene Kamer"),
        reverse("proposals:archive", args=['AK']),
    ),
    MenuItem(
        _("Alle studies bekijken van de Linguïstiek Kamer"),
        reverse("proposals:archive", args=['LK']),
    ),
    MenuItem(
        _("Site-export"),
        reverse("proposals:archive_export"),
        check=lambda x: is_secretary(x.user),
    ),
)


Menu.add_item(
    "main",
    MenuItem(
        _("Archief"),
        "#",
        slug='archive',  # needed for sub-menu!
        children=archive_menu,
        check=lambda x: x.user.is_authenticated,
    )
)
