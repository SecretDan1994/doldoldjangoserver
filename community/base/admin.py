from django.contrib import admin
from ordered_model.admin import OrderedTabularInline, OrderedModelAdmin

from .models import SiteSetting, SideBarEntry, GenericPostsByViewAndPos, GenericPost, GenericPostsViewsThroughModel
from .models import *


class a(OrderedModelAdmin):
    list_display = ("name", 'move_up_down_links',)

class b(OrderedModelAdmin):
    list_display = ("subject", 'move_up_down_links',)

class c(OrderedModelAdmin):
    list_display = ("__str__", 'move_up_down_links',)

class SideBarEntryAdmin(OrderedModelAdmin):
    list_display = ("name", 'move_up_down_links',)

class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "value",)
    readonly_fields = ('name', 'description',)
    ordering = ('name',)

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

class GenericPostsViewsThroughModelInline(OrderedTabularInline):
    model = GenericPostsViewsThroughModel
    fields = ('post', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    extra = 1
    ordering = ('order',)#		order_by = ("view_object_name", "position")

class GenericPostAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = (GenericPostsViewsThroughModelInline, )

    readonly_fields = ('_message_metadata',)
    
    def get_urls(self):
        urls = super(GenericPostAdmin, self).get_urls()
        for inline in self.inlines:
            if hasattr(inline, 'get_urls'):
                urls = inline.get_urls(self) + urls
        return urls

admin.site.register(SideBarEntry, SideBarEntryAdmin)
admin.site.register(SiteSetting, SiteSettingAdmin)

admin.site.register(GenericPost, GenericPostAdmin)
admin.site.register(GenericPostsByViewAndPos)

admin.site.register(Section, a)
admin.site.register(Article, b)

admin.site.register(SectionArticle, c)
