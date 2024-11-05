from copy import copy

from django.utils.translation import gettext as _

from main.utils import renderable

from .stepper_helpers import (
    PlaceholderItem,
    StepperItem,
)

from .checkers import ProposalTypeChecker

from tasks.forms import SessionOverviewForm
from studies.forms import StudyForm, StudyDesignForm, StudyEndForm
from observations.forms import ObservationForm
from interventions.forms import InterventionForm

from proposals.utils.validate_sessions_tasks import validate_sessions_tasks
from attachments.utils import AttachmentSlot
from attachments.kinds import desiredness


class Stepper(renderable):

    template_name = "base/stepper.html"

    def __init__(
        self,
        proposal,
        request=None,
    ):
        self.proposal = proposal
        self.starting_checkers = [
            ProposalTypeChecker,
        ]
        # The stepper keeps track of the request to determine
        # which item is current
        self.request = request
        self.items = []
        self.current_item_ancestors = []
        self._attachment_slots = []
        self.check_all(self.starting_checkers)

    @property
    def attachment_slots(
        self,
    ):
        """
        Appends unmatched attachments as extra slots to the internal
        list _attachment_slots.
        """
        extra_slots = []
        objects = [self.proposal] + list(self.proposal.study_set.all())
        for obj in objects:
            success = True
            while success:
                exclude = [s.attachment for s in self._attachment_slots] + [
                    s.attachment for s in extra_slots
                ]
                empty_slot = AttachmentSlot(
                    obj,
                    force_desiredness=desiredness.EXTRA,
                )
                success = empty_slot.match(exclude=exclude)
                if success:
                    extra_slots.append(empty_slot)
        return self._attachment_slots + extra_slots

    def get_context_data(self):
        context = super().get_context_data()
        # Provide the stepper bubble classes in order
        # of descending size
        bubble_list = [
            "stepper-bubble-largest",
            "stepper-bubble-large",
            "stepper-bubble-medium",
            "stepper-bubble-small",
            "stepper-bubble-smallest",
        ]
        context.update(
            {
                "stepper": self,
                "bubble_size": bubble_list,
            }
        )
        return context

    def get_resume_url(self):
        """
        Returns the url of the first page that requires attention,
        that being either a page with an error or an incomplete page.
        """
        for item in self.items:
            if not item.is_complete:
                return item.get_url()

    def build_stepper(
        self,
    ):
        """
        The meat and potatoes of the stepper. Returns a list of top-level
        StepperItems to be rendered in the template.
        """
        # In building the stepper we will be editing this layout in-place,
        # which means we need to make a copy. Otherwise we're editing the
        # original RegularProposalLayout which causes strange behaviour
        # when it is in use by any other steppers.
        layout = copy(getattr(self, "layout", False))
        if not layout:
            # Layout should be set before building the stepper
            # by something like ProposalTypeChecker
            raise RuntimeError(
                "Base layout was never defined for this stepper",
            )
        # First, insert all items into the layout & let them figure out their
        # own styling
        for item in self.items:
            # Only check item.is_current until there is a current item found
            self.item_is_current_check(item)
            self._insert_item(layout, item)
        # Second, replace all remaining empty slots in the layout
        # by PlaceholderItems
        self._insert_placeholders(layout)
        return layout

    def _insert_item(self, layout, new_item):
        # We're only concerned with top-level items, children can sort
        # themselves out
        if new_item.parent:
            return new_item.parent.children.append(
                new_item,
            )
        # Step through the layout looking for empty slots, which are
        # represented by tuples of locations and titles
        for index, slot in enumerate(layout):
            # If the slot is already filled with an actual item, just
            # skip it
            if type(slot) is not tuple:
                continue
            # If the slot location matches that of our new_item, replace
            # this slot with the item
            if new_item.location == slot[0]:
                layout.insert(index, new_item)
                layout.remove(slot)

    def _insert_placeholders(self, layout):
        # Step through the remaining slots in the layout
        for index, slot in enumerate(layout):
            # Skip slots that are already items
            if isinstance(slot, StepperItem):
                continue
            # Remaining empty slots are replaced by placeholders
            placeholder = PlaceholderItem(
                self,
                title=slot[1],
            )
            layout.insert(index, placeholder)
            layout.remove(slot)
        return layout

    def check_all(self, next_checkers):
        # No more checkers means we are done
        if next_checkers == []:
            return True
        # Instantiate next checker
        # and give it access to the stepper
        current = next_checkers.pop(0)(self)
        # Run the check method
        # and gather new checkers from its output
        new_checkers = current.check()
        # Combine the lists, new checkers come first
        next_checkers = new_checkers + next_checkers
        # Recurse until next_checkers is empty
        return self.check_all(next_checkers)

    def item_is_current_check(self, item):
        """
        Sets current_item and current_item_ancestor attributes, when these
        are found, and set the is_expanded attribute to True for these
        items.
        """
        if not self.current_item_ancestors:
            if item.is_current(self.request):
                item.css_classes.add("active")
                self.current_item_ancestors = item.get_ancestors()
                for item in self.current_item_ancestors:
                    item.is_expanded = True

    def add_slot(self, slot):
        """
        Append an attachment slot to the stepper. As an intermediate step,
        we attempt to match the slot to an existing attachment. We do this
        here because the stepper has ownership of the already matched
        attachments to be excluded from matching.
        """
        exclude = [slot.attachment for slot in self._attachment_slots]
        slot.match(exclude)
        self._attachment_slots.append(slot)

    def has_multiple_studies(
        self,
    ):
        """
        Returns True if the proposal has more than one trajectory (study).
        """
        num_studies = self.proposal.study_set.count()
        return num_studies > 1

    def get_form_errors(self):
        """
        A method providing validation of all the forms making up the proposal.
        It return a list of dicts, with url's and formatted page name's
        for pages with errors on them.
        """

        troublesome_pages = []
        study_forms = [
            StudyForm,
            StudyEndForm,
            StudyDesignForm,
            InterventionForm,
            ObservationForm,
            SessionOverviewForm,
        ]

        for item in self.items:
            if item.get_errors(include_children=False):
                if self.has_multiple_studies() and item.form_class in study_forms:
                    page_name = f"{item.parent.title}: {item.title}"
                else:
                    page_name = item.title
                troublesome_pages.append(
                    {
                        "url": item.get_url(),
                        "page_name": page_name,
                    }
                )
            # As individual sessions and tasks are not represented in the
            # stepper, these are validated through an external function.
            if hasattr(item, "form_class") and item.form_class == SessionOverviewForm:
                troublesome_pages.extend(
                    validate_sessions_tasks(item.study, self.has_multiple_studies())
                )

        return troublesome_pages


RegularProposalLayout = [
    ("create", _("Basisgegevens")),
    ("wmo", _("WMO")),
    ("studies", _("Trajecten")),
    ("attachments", _("Documenten")),
    ("data_management", _("Datamanagement")),
    ("submit", _("Indienen")),
]

PreApprProposalLayout = [
    ("create", _("Basisgegevens")),
    ("submit", _("Indienen")),
]

PreAssProposalLayout = [
    ("create", _("Basisgegevens")),
    ("wmo", _("WMO")),
    ("submit", _("Indienen")),
]
