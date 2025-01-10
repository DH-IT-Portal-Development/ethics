from django import template
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from main.utils import get_static_file
from proposals.models import Proposal
from studies.models import Study

register = template.Library()


class CompareLinkNode(template.Node):
    def __init__(self, type, obj, attribute=""):
        self.type = type
        self.obj = template.Variable(obj)
        self.attribute = attribute

    def _get_documents_url(self, obj, proposal: Proposal):
        if obj.study:
            parent_study = proposal.parent.study_set.get(
                order=obj.study.order,
            )  # type: Study

            args = [parent_study.documents.pk, obj.pk, self.attribute]

        else:
            old_set = proposal.parent.documents_set.filter(study=None)
            new_set = proposal.documents_set.filter(study=None)
            new_index = -1
            for i, el in enumerate(new_set):
                if el.pk == obj.pk:
                    new_index = i

            try:
                old_obj = old_set[new_index].pk
            except (IndexError, AttributeError):
                return None

            args = [old_obj, obj.pk, self.attribute]

        return reverse("proposals:compare_documents", args=args)

    def _get_observation_url(self, obj, proposal):
        order = obj.study.order
        try:
            old_study = proposal.parent.study_set.get(order=order)
        except Proposal.DoesNotExist:
            return None

        if old_study.get_observation():
            if not obj.approval_document or not old_study.observation.approval_document:
                return None

            args = [old_study.observation.pk, obj.pk]

            return reverse("proposals:compare_observation_approval", args=args)

        return None

    def render(self, context):
        "This function gets called when the template gets rendered"

        title = _("Toon verschillen")
        img = get_static_file("proposals/images/arrow_divide.png")
        obj = self.obj.resolve(context)

        # Documents associated with a study
        # or extra Documents objects
        if self.type == "documents":
            proposal = obj.proposal
            if not proposal.parent:
                return ""

            url = self._get_documents_url(obj, proposal)

        # Observations, possibly unused
        elif self.type == "observation":
            proposal = obj.study.proposal
            if not proposal.parent:
                return ""

            url = self._get_observation_url(obj, proposal)

        # General proposal docs
        elif self.type == "proposal":
            if not obj.parent:
                return ""

            args = [
                obj.parent.pk,
                obj.pk,
                self.attribute,
            ]

            url = reverse("proposals:compare_proposal_docs", args=args)

        # METC Decision files
        elif self.type == "wmo":
            if not obj.proposal.parent or not obj.proposal.parent.wmo:
                return ""

            args = [
                obj.proposal.parent.wmo.pk,
                obj.pk,
            ]

            url = reverse("proposals:compare_wmo_decision", args=args)
        else:
            return ""

        if url is None:
            return ""

        return (
            '<a href="{url}" target="_blank" class="icon-link">'
            '<img src="{img}" title="{title}">'
            "</a>".format(
                url=url,
                img=img,
                title=title,
            )
        )


@register.tag
def get_compare_link(parser, token):
    """This function splits up the arguments given inside the tag
    and passes them on to the CompareLinkNode class"""

    parts = token.split_contents()

    if not (3 <= len(parts) < 5):
        raise template.TemplateSyntaxError(
            "'get_compare_link' tag must be of the form: {% get_compare_link "
            "<type> <object> (<attribute>) %}"
        )

    args = {
        "type": parts[1],
        "obj": parts[2],
    }

    if len(parts) == 4:
        args["attribute"] = parts[3]

    return CompareLinkNode(**args)
