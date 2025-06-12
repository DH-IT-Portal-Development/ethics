from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

from main.utils import is_secretary, can_view_archive, is_authenticated, get_user

new_proposal_menu = (
    MenuItem(
        _("Nieuwe aanvraag starten"),
        reverse("proposals:start"),
    ),
    MenuItem(
        _("Nieuwe aanvraag starten op basis van een kopie van een oude aanvraag"),
        reverse("proposals:copy"),
    ),
    MenuItem(
        _("Nieuwe aanvraag starten voor (al dan niet goedgekeurde) subsidieaanvragen"),
        reverse("proposals:start_pre"),
    ),
    MenuItem(
        _(
            "Nieuwe aanvraag starten (die al goedgekeurd is door een andere "
            "ethische toetsingscomissie)"
        ),
        reverse("proposals:start_pre_approved"),
    ),
    MenuItem(
        _("Nieuwe oefenaanvraag starten"),
        reverse("proposals:start_practice"),
    ),
    MenuItem(
        _("Maak een revisie van een bestaande aanvraag"),
        reverse("proposals:copy_revision"),
    ),
    MenuItem(
        _("Maak een amendement van een al goedgekeurde aanvraag"),
        reverse("proposals:copy_amendment"),
    ),
)

Menu.add_item(
    "main",
    MenuItem(
        _("Nieuwe aanvraag"),
        "#",
        slug="new-studies",  # needed for sub-menu!
        children=new_proposal_menu,
        check=is_authenticated,
    ),
)

my_proposals_menu = (
    MenuItem(
        _("Al mijn aanvragen"),
        reverse("proposals:my_archive"),
    ),
    MenuItem(
        _("Mijn conceptaanvragen"),
        reverse("proposals:my_concepts"),
    ),
    MenuItem(
        _("Mijn oefenaanvragen"),
        reverse("proposals:my_practice"),
    ),
    MenuItem(
        _("Mijn ingediende aanvragen"),
        reverse("proposals:my_submitted"),
    ),
    MenuItem(
        _("Mijn afgehandelde aanvragen"),
        reverse("proposals:my_completed"),
    ),
    MenuItem(
        _("Mijn aanvragen als eindverantwoordelijke"),
        reverse("proposals:my_supervised"),
    ),
)

Menu.add_item(
    "main",
    MenuItem(
        _("Mijn aanvragen"),
        reverse("proposals:my_archive"),
        slug="my-studies",  # needed for sub-menu!
        children=my_proposals_menu,
        check=is_authenticated,
    ),
)

archive_menu = (
    MenuItem(
        _("Bekijk alle goedgekeurde aanvragen van de Algemene Kamer"),
        reverse("proposals:archive", args=["AK"]),
        check=lambda request: can_view_archive(get_user(request)),
    ),
    MenuItem(
        _("Bekijk alle goedgekeurde aanvragen van de Linguïstiek Kamer"),
        reverse("proposals:archive", args=["LK"]),
        check=lambda request: can_view_archive(get_user(request)),
    ),
    MenuItem(
        _("Site-export"),
        reverse("proposals:archive_export"),
        check=lambda request: is_secretary(get_user(request)),
    ),
)


Menu.add_item(
    "main",
    MenuItem(
        _("Archief"),
        "#",
        slug="archive",  # needed for sub-menu!
        children=archive_menu,
        check=lambda request: can_view_archive(get_user(request)),
    ),
)
