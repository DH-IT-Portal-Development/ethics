from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from menu import Menu, MenuItem

help_menu = (
    MenuItem(
        _("FETC-GW website"),
        _("http://fetc-gw.wp.hum.uu.nl/"),
        open_in_new_tab=True,
    ),
    MenuItem(
        _("Reglement FETC-GW"),
        _("https://fetc-gw.wp.hum.uu.nl/reglement-fetc-gw/"),
        open_in_new_tab=True,
    ),
    MenuItem(
        _("Informed consent formulieren"),
        _("https://intranet.uu.nl/documenten-ethische-toetsingscommissie-gw"),
        open_in_new_tab=True,
    ),
    MenuItem(
        _("FAQs"),
        reverse("faqs:list"),
    )
)

Menu.add_item("main", MenuItem(_('Help'),
                               "#",
                               children=help_menu,
                               exact_url=True,
                               ))

