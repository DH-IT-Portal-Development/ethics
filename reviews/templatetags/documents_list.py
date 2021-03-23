from django import template

register = template.Library()

@register.inclusion_tag('documents_list.html')
def documents_list(review):
    return {'review': review}
