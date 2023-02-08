from django import template
from django.apps import apps
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from studies.utils import check_has_adults, check_necessity_required

register = template.Library()

@register.filter
def needs_details(selected_values, field='needs_details'):
    result = False
    for sv in selected_values:
        if getattr(sv, field):
            result = True
            break
    return result


@register.filter
def has_adults(study):
    age_groups = study.age_groups.values_list('id', flat=True)
    return check_has_adults(age_groups)


@register.filter
def necessity_required(study):
    age_groups = study.age_groups.values_list('id', flat=True)
    return check_necessity_required(study.proposal, age_groups, study.has_traits, study.legally_incapable)


@register.simple_tag
def show_yesno(doubt=False):
    result = '<ul>'
    result += '<li>{}</li>'.format('ja')
    result += '<li>{}</li>'.format('nee')
    if doubt:
        result += '<li>{}</li>'.format('twijfel')
    result += '</ul>'
    return mark_safe(result)


@register.simple_tag
def show_yesnodoubt():
    return show_yesno(True)


class StudyDocumentsNode(template.Node):
    """
    This node handles adding a documents object for a given study, by first getting the study object from the context.
    """

    def __init__(self, var_name, study):
        self.var_name = var_name
        self.var_value = template.Variable(study)

    def render(self, context):
        study = self.var_value.resolve(context)
        if study is not None:
            try:
                context[self.var_name] = apps.get_model("studies", "Documents").objects.get(study=study)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                context[self.var_name] = None
        return u""


@register.tag
def get_study_documents(parser, token):
    """
    Adds a variable to the context with the documents object for the specified study

    Usage:
    {% get_study_documents VARIABLE_NAME STUDY_OBJECT %}
    params:
    VARIABLE_NAME: the name of the variable to store the object in
    STUDY_OBJECT: the variable which contains the study object
    """
    parts = token.split_contents()

    return StudyDocumentsNode(parts[1], parts[2])


class ExtraDocumentsNode(template.Node):
    """
    This node handles adding a documents object for a given study, by first getting the study object from the context.
    """

    def __init__(self, var_name, study):
        self.var_name = var_name
        self.var_value = template.Variable(study)

    def render(self, context):
        proposal = self.var_value.resolve(context)
        context[self.var_name] = apps.get_model("studies", "Documents").objects.filter(proposal=proposal, study=None).all()

        return u""


@register.tag
def get_extra_documents(parser, token):
    """
    Adds a variable to the context with a list of extra documents objects for the specified proposal

    Usage:
    {% get_study_documents VARIABLE_NAME PROPOSAL_OBJECT %}
    params:
    VARIABLE_NAME: the name of the variable to store the list in
    PROPOSAL_OBJECT: the variable which contains the proposal object
    """
    parts = token.split_contents()

    return ExtraDocumentsNode(parts[1], parts[2])

