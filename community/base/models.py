from django.db import models
from ordered_model.models import OrderedModel
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.core.validators import *
from django.contrib.auth.models import Permission
from .util import message_metadata_factory, site_setting_ensure
from django.core.exceptions import PermissionDenied
import re

site_setting_ensure("DISABLED", "false", "If true website is only accessible to Super Admins")
site_setting_ensure("AUTHOR", "Doldol @ http://steamcommunity.com/id/Doldol/", "The Main Developer, Doldol @ http://steamcommunity.com/id/Doldol/")
site_setting_ensure("NOTICE", "", "Notice displayed at all times")
site_setting_ensure("BASE_TITLE", "The Elevated Gaming Network", "The Base title of the whole site")
site_setting_ensure("META_KEYWORDS", "", "Meta header keywords")
site_setting_ensure("META_DESCRIPTION", "", "Meta header site description")


class MessageMetaField(JSONField):
	description = "Meta data for message text"

	def __init__(self, *args, **kwargs):
		kwargs['default'] = message_metadata_factory
		super().__init__(*args, **kwargs)

	@property
	def hashtags(self):#are search tags
		return self["hashtags"]

	@hashtags.setter
	def hashtags(self, value):
		self["hashtags"] = value

	@property
	def user_mentions(self):
		return self["user_mentions"]

	@user_mentions.setter
	def user_mentions(self, value):
		self["user_mentions"] = value

	@property
	def group_mentions(self):
		return self["group_mentions"]

	@group_mentions.setter
	def group_mentions(self, value):
		self["group_mentions"] = value


class BBCodeField(JSONField):
	pass

class BaseMessage(models.Model):
	title = models.CharField(max_length=200)
	metadata = MessageMetaField()

	class Meta:
		abstract=True

class Section(models.Model):
	name = models.CharField(max_length=200)

class Article(models.Model):
	subject = models.CharField(max_length=200)
	sections = models.ManyToManyField(Section, through='SectionArticle')

class SectionArticle(OrderedModel):
	section = models.ForeignKey(Section)
	article = models.ForeignKey(Article)
	order_with_respect_to = 'section'

	class Meta(OrderedModel.Meta):
		pass

class SiteSetting(models.Model):
	name = models.CharField(max_length=100, unique=True)
	value = JSONField()
	description = models.TextField(max_length=1000, blank=True, null=True)

	def __str__(self):
		return self.name

	@property
	def value_preview(self):
		return str(self.value)[:25]

	def save(self, *args, **kwargs):
		cache.set("setting-{0}".format(self.name), self.value)
		super().save(*args, **kwargs)

	@classmethod
	def get_setting(clas, name):
		value = cache.get("setting-{0}".format(name))
		if not value:
			value = clas.objects.get(name=name).value
			cache.set("setting-{0}".format(name), value)
		return value

	@classmethod
	def ensure(clas, name, default=None, description=None):
		if not cache.get("setting-{0}".format(name)):
			if not clas.objects.filter(name=name).exists():
				setting = clas(name=name, value=default,  description=description)
				setting.save()

class SideBarEntry(OrderedModel):
	name = models.CharField(max_length=100)
	location = models.CharField(max_length=500, blank=True, null=True)
	parent = models.ForeignKey('self', related_name="children", blank=True, null=True)
	faicon = models.CharField(max_length=20, blank=True, null=True)
	styling = models.CharField(max_length=255, blank=True, null=True)
	order_with_respect_to = 'parent'

	def __str__(self):
		return "{0}.{1}".format(self.parent, self.name)


class GenericPostsByViewAndPos(models.Model):
	view_object_name = models.CharField(max_length=100, unique=True) # name of view object
	position = models.PositiveSmallIntegerField()

	def __str__(self):
		return "GenericPosView.{0}".format(self.id)

	class Meta:
		unique_together = (("view_object_name", "position"),)


class GenericPost(models.Model):
	title = models.CharField(max_length=100)
	created = models.DateTimeField(verbose_name='Date created', default=timezone.now)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='generic_posts_from')
	changed_by = models.ForeignKey('auth.User')
	message_html =  models.TextField(verbose_name='Message in HTML', unique=True, max_length=50000)
	message = models.TextField(verbose_name='Message in BBCode', unique=True, max_length=40000)
	parent_views = models.ManyToManyField(GenericPostsByViewAndPos, through="GenericPostsViewsThroughModel")
	_message_metadata = JSONField(default=message_metadata_factory)

	history = HistoricalRecords()

	def __str__(self):
		return "{0}.{1}".format(self.id, self.title)

	def save(self, *args, **kwargs):
		# calc metadata
		super().save(*args, **kwargs)

	@property
	def _history_user(self):
		return self.changed_by

	@_history_user.setter
	def _history_user(self, value):
		self.changed_by = value

	@property
	def hashtags(self):
		return self._message_metadata["hashtags"]

	@hashtags.setter
	def hashtags(self, value):
		self._message_metadata["hashtags"] = value

	@property
	def user_mentions(self):
		return self._message_metadata["user_mentions"]

	@user_mentions.setter
	def user_mentions(self, value):
		self._message_metadata["user_mentions"] = value

	@property
	def group_mentions(self):
		return self._message_metadata["group_mentions"]

	@group_mentions.setter
	def group_mentions(self, value):
		self._message_metadata["group_mentions"] = value

class GenericPostsViewsThroughModel(OrderedModel):
	view = models.ForeignKey(GenericPostsByViewAndPos)
	post = models.ForeignKey(GenericPost)
	order_with_respect_to = 'view'

	class Meta:
		ordering = ("view", 'order')