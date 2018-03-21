from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from .models import Category, Forum, Topic, Post, Owner

class CategoryAdmin(OrderedModelAdmin):
	list_display = ('title', 'move_up_down_links')
	readonly_fields = ('slug',)

class ForumAdmin(OrderedModelAdmin):
	list_display = ('title', "description", 'move_up_down_links')
	readonly_fields = ('description_html', "slug")

class PostAdmin(OrderedModelAdmin):
	readonly_fields = ('slug',)

class TopicAdmin(OrderedModelAdmin):
	readonly_fields = ('slug',)


admin.site.register(Post, PostAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Owner)
admin.site.register(Forum, ForumAdmin)
admin.site.register(Category, CategoryAdmin)
