from django import template

register = template.Library()


@register.filter
def comma_replace(value):
    values = value.split(',')

    text = ''
    for item in values:
        if item != '':
            text += item.strip() + ",\\newline "

    # if text != '':
    #     text = '\makecell{%s}' % text

    return text
