from django import template
from django.conf import settings
from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def in_linguistics_chamber(current_user):
    """
    Check whether the current user is in the 'ETCL' or 'Secretaris' group
    """
    return Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER) in current_user.groups.all() or \
        Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()

@register.filter
def in_general_chamber(current_user):
    """
    Check whether the current user is in the 'FETC' or 'Secretaris' group
    """
    return Group.objects.get(name=settings.GROUP_GENERAL_CHAMBER) in current_user.groups.all() or \
        Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()


@register.filter
def is_secretary(current_user):
    """
    Check whether the current user is in the 'Secretary' group
    """
    return Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()

class SetVarNode(template.Node):
    """
    This is a very simple node that just assigns a given value to a given variable in the template context
    """

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        context[self.var_name] = self.var_value

        return u""

@register.tag(name='set')
def set_var(parser, token):
    """
    {% set some_var = '123' %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form: {% set <var_name> = <var_value> %}")

    return SetVarNode(parts[1], parts[3])

class Counter:
    """
    Very simple counter used in the counter tag
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __le__(self, other):
        return other >= self.value

    def __lt__(self, other):
        return other > self.value

    def __ge__(self, other):
        return other <= self.value

    def __gt__(self, other):
        return other < self.value

    def __eq__(self, other):
        return other == self.value

    def increment(self):
        """
        Use this to increment the counter. Please note that you should use {{ c.incement }}, not {% c.increment %},
        as this is not a tag method
        :return: Empty string
        """
        self.value = self.value + 1
        return u""

@register.tag
def counter(parser, token):
    """
    Creates a counter object under a specified variable name, optionally with a starting number. By default it starts
    counting at 0.

    Usage:
    {% counter VAR_NAME %}
    or
    {% counter VAR_NAME STARTING_VALUE %} (to specify the starting value, must be an int or int in a string)

    To increment:
    {{ VAR_NAME.increment }}

    To display the value:
    {{ VAR_NAME }}
    """
    parts = token.split_contents()

    # We default to a starting value
    start_value = 0

    # If we have 3 parts, the third part should be interpreted as the desired starting value
    if len(parts) == 3:
        # Try to parse it to an int, throw a syntax error if we can't
        try:
            start_value = int(parts[2])
        except ValueError:
            raise template.TemplateSyntaxError("Counter start value is not an integer! ")

    # We need 2 or 3 parts to count as a valid usage
    if 1 < len(parts) <= 3:
        var_name = parts[1]

        # Under the hood we actually just use the same node as assign uses, we just need to assign a var with a counter
        return SetVarNode(var_name, Counter(start_value))
    else:
        raise template.TemplateSyntaxError("'counter' tag must be of the form: {% counter <var_name> (<start_value>) %}")


