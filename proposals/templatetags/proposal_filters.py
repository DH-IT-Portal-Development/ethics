from django import template

register = template.Library()


@register.filter
def selected_labels(form, field):
    return [label for value, label in form.fields[field].choices if value in form[field].value()]
