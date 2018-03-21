from django.contrib import admin

from .models import UserSettingValidator, UserSetting,  UserSettingData

# Register your models here.
admin.site.register(UserSettingValidator)
admin.site.register(UserSettingData)

admin.site.register(UserSetting)
