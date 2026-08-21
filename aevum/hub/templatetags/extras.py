from django import template
from django.utils.text import slugify as dj_slugify
register = template.Library()

@register.filter
def split(value, sep):
    if value is None: return []
    return [s.strip() for s in str(value).split(sep) if s.strip()]

@register.filter
def get(d, key):
    if not d: return []
    if hasattr(d, 'get'): return d.get(key, [])
    return []

@register.filter
def slugify(value):
    return dj_slugify(value or "")
