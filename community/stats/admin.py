from django.contrib import admin
from .models import GameServer, LogTag, ServerLog, Game, Team

from ordered_model.admin import OrderedModelAdmin
# Register your models here.

class GameServerAdmin(OrderedModelAdmin):
    readonly_fields = ('secret_key', 'connected')
    ordering = ('order',)

    list_display = ('__str__', 'move_up_down_links')

class ServerLogAdmin(admin.ModelAdmin):
    ordering = ('-time',)
    list_filter = (
        ('server', admin.RelatedOnlyFieldListFilter),
        ('tag', admin.RelatedOnlyFieldListFilter),
        ('kind'),
        ('time'),
    )

    list_display = ('__str__', "tag", "kind", "time")

admin.site.register(GameServer, GameServerAdmin)
admin.site.register(LogTag)
admin.site.register(ServerLog, ServerLogAdmin)
admin.site.register(Game)
admin.site.register(Team)
