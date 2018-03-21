from django import template

from ..util import user_setting_ensure
from ..models import UserSetting

register = template.Library()

@register.simple_tag
def user_setting(user, setting):
    return UserSetting.get_user_setting(setting=setting, user=user)