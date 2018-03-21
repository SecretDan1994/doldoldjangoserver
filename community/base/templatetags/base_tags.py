from django import template

from ..util import site_settings, get_preferred_name_by_instance

register = template.Library()

@register.simple_tag
def site_setting(key):
    return site_settings.__getattr__(key)

@register.simple_tag
def url_replace(request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value
    return dict_.urlencode()

@register.filter
def preferred_name(value):
    return get_preferred_name_by_instance(value)