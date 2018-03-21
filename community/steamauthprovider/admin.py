from django.contrib import admin

from . import models
# Register your models here.
admin.site.register(models.SteamUser)
#admin.site.register(models.SteamUserMetaData)