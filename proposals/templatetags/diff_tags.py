from django import template


register = template.Library()


@register.filter(name='zip_equalize_lists')
def zip_equalize_lists(a, b):
    """
    A zip implementation which will not stop when reaching the end of the
    smallest list, but will append None's to the smaller list to fill the gap
    """
    try:
        a = list(a)
    except TypeError:
        a = [a]
    try:
        b = list(b)
    except TypeError:
        b = [b]

    a_len = len(a)
    b_len = len(b)
    diff = abs(a_len - b_len)

    if a_len < b_len:
        for _ in range(diff):
            a.append(None)

    if b_len < a_len:
        for _ in range(diff):
            b.append(None)

    return zip(a, b)
