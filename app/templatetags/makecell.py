import json
import ast
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def makecell(value):
    utf8string = value.encode("utf-8")
    values = ast.literal_eval(utf8string)

    text = ''
    for item in values:
        print item
        if item != '':
            text += item.strip() + ",\\newline "

    # if text != '':
    #     text = '\makecell{%s}' % text

    return text