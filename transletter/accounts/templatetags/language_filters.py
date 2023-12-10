from django import template

from transletter.utils import get_available_langs

__all__ = ()

register = template.Library()


@register.filter
def language_name(code):
    for language_code, language_name in get_available_langs():
        if code == language_code:
            return language_name
    return code
