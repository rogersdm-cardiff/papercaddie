from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def cite(value):
    return "\citeauthor{"+value+"} \citeyear{"+value+"} \cite{"+value+"}"