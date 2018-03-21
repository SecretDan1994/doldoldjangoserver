from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from base.util import get_page, get_preferred_name_by_instance, site_settings
from .models import Category, Forum, Topic, Post

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from django.utils import timezone

def index(request):
	forum_struct = Category.objects.all().select_related("owns").order_by('order')

	forum_stats = cache.get("forum-stats")
	if forum_stats == None:
		forum_stats = {}
		forum_stats["active_session_count"] = Session.objects.filter(expire_date__gte=timezone.now()).count()
		forum_stats["active_user_count"] = User.objects.filter(is_active=True).count()
		forum_stats["topic_count"] = Topic.objects.filter(soft_deleted=False).count()
		forum_stats["post_count"] = Post.objects.filter(soft_deleted=False, topic__soft_deleted=False).count()
		forum_stats["forum_count"] = Forum.objects.all().count()
		forum_stats["cat_count"] = Category.objects.all().count()
		cache.set("forum-stats", forum_stats, 5*50)

	context = {
		'forum_struct': forum_struct,
		'forum_stats': forum_stats,
	}
	return render(request, 'forum/index.html', context)

def view_category(request, slug=None):
	category = Category.objects.get(slug=slug)
	context = {
		"category": category,
		'forum_struct_page': get_page(category.get_children(), request, 25),
	}
	return render(request, 'forum/category.html', context)

def view_forum(request, slug=None,):
	# get sort mode from cookies  sortmode=2
	mode = 2 
	forum = Forum.objects.get(slug=slug)
	# get sort order
	#check perm
	context = {
		"forum": forum,
		"nav_help": [x for x in forum.yield_parents_upwards()],
		'forum_struct_page': get_page(forum.get_children(), request, 25),
		'topic_struct_page': get_page(forum.get_topics_by_sort_order(mode=mode), request, 25),
	}
	return render(request, 'forum/forum.html', context)

def view_topic(request, slug=None):
	# get sort mode from cookies  sortmode=2
	topic = Topic.objects.get(slug=slug)
	context = {
		"topic": topic,
		'post_struct_page': get_page(topic.posts.all(), request, 25),
	}
	return render(request, 'forum/topic.html', context)

def view_post(request, slug=None):
	pass