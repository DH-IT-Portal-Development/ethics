from django import template
from django.conf import settings
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='zip')
def zip_lists(a, b):
  return zip(a, b)

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


class CounterNode(template.Node):

    def __init__(self, name, action, **kwargs):
        self.name = name
        self.action = action
        self.kwargs = kwargs

    def _get_counter_key(self):
        """Returns the key for this counter object in the render_context"""
        return "counter_{}".format(self.name)

    def render(self, context):
        key = self._get_counter_key()

        # Storing it in render_context makes sure we are thread-safe
        # The documentation uses 'self' as a key, but that only refers
        # to that occurrence of the tag. We want a tag to reference to a
        # thread-global counter, so we use a custom made key
        if key not in context.render_context or self.action == 'create':
            context.render_context[key] = Counter(self.kwargs.get('value', 0))

        if self.action == 'store':
            context[self.name] = context.render_context[key].value

        if self.action == 'increment':
            for i in range(self.kwargs.get('value', 1)):
                context.render_context[key].increment()

        if self.action == 'value':
            return str(context.render_context[key])

        return ""


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
        """Do not use in templates! (If you even can...)"""
        self.value = self.value + 1

@register.tag
def counter(parser, token):
    """
    Creates a counter, optionally with a starting number. By default it starts
    counting at 0.

    Usage:

    To create:
    {% counter NAME create %}
    or
    {% counter NAME create STARTING_VALUE %} (to specify the starting value,
    must be an int or int in a string)

    To increment:
    {% counter NAME increment (VALUE) %}
    (VALUE is optional, and can be used to increment the counter by the given
    value).

    To display the value:
    {% counter NAME value %}

    Alternatively, you can store the current value in a template variable:
    {% counter NAME store %}
    It's value will be stored into a variable called NAME.
    Note: this might not be thread-safe!
    """
    parts = token.split_contents()

    # We expect two or three arguments
    if 1 <= len(parts) <= 2 or len(parts) > 4:
        raise template.TemplateSyntaxError("'counter' tag must be of the "
                                           "form: {% counter <name> <action> ("
                                           "value>) %}")

    kwargs = {
        'name': parts[1],
        'action': parts[2],
    }

    # If we have 4 parts, the third part should be interpreted as 'value'
    if len(parts) == 4:
        # Try to parse it to an int, throw a syntax error if we can't
        try:
            kwargs['value'] = int(parts[3])
        except ValueError:
            raise template.TemplateSyntaxError("Counter value is not an integer! ")

    return CounterNode(**kwargs)

