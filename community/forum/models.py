from django.db import models
from django.db.models import Count
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from autoslug import AutoSlugField
from simple_history.models import HistoricalRecords
from ordered_model.models import OrderedModel
from base.util import message_metadata_factory
from django.urls import reverse
from django.utils import timezone
from django import forms

from django.core.exceptions import ObjectDoesNotExist

class ChoiceArrayField(ArrayField):
    """
    A field that allows us to store an array of choices.
    
    Uses Django 1.9's postgres ArrayField
    and a MultipleChoiceField for its formfield.
    
    Usage:
        
        choices = ChoiceArrayField(models.CharField(max_length=...,
                                                    choices=(...,)),
                                   default=[...])
    """

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        # Skip our parent's formfield implementation completely as we don't
        # care for it.
        # pylint:disable=bad-super-call
        return super(ArrayField, self).formfield(**defaults)

class Owner(models.Model):
	category = models.OneToOneField("Category", null=True, blank=True, related_name="owns", on_delete=models.CASCADE)
	forum = models.OneToOneField("Forum", null=True, blank=True, related_name="owns", on_delete=models.CASCADE)

	def __str__(self):
		return "{0}: {1}".format(self.target._meta.verbose_name.title(), self.target.title)

	def save(self, **kwargs):
		assert [self.category, self.forum].count(None) == 1
		return super().save(**kwargs)

	@property
	def target(self):
		if self.category is not None:
			return self.category
		if self.forum is not None:
			return self.forum
		raise AssertionError("Neither 'category' nor 'forum' is set")


# add tag cloud for more than forum posts
class Category(OrderedModel):
	title = models.CharField(verbose_name='Title', unique=False, max_length=100)
	slug = AutoSlugField(unique=True, populate_from="title", sep=".")
	icon = models.ImageField(upload_to='forum_icons', blank=True, null=True) 

	def __str__(self):
		return self.slug

	def get_children(self):
		try:
			return self.owns.children.all()
		except ObjectDoesNotExist:
			return Category.objects.none()

	def get_absolute_url(self):
		return reverse('forum:view_category', args=(self.slug,))

	class Meta(OrderedModel.Meta):
		verbose_name_plural = "Categories"
		permissions = (
			("view_category", "Can view category"),
		)


class Forum(OrderedModel):
	VOTING_CHOICES = (
		(True, 'Enabled'),
		(False, 'Disabled'),
	)
	MODE_CHOICES = (
		(0, 'user'),
		(1, 'classic'),
		(2, 'tree'),
		(3, 'classic+votes'),
		(4, 'tree+votes'),
	)
	SORT_CHOICES = (
		(0, 'user'),
		(1, 'hot'),
		(2, 'creation'),
		(3, 'reply'),
		(4, 'votes'),
		(5, 'old')
	)
	title = models.CharField(verbose_name='Title', unique=False, max_length=100)
	slug = AutoSlugField(unique=True, populate_from="title", sep=".")
	description_html = models.TextField(verbose_name='Description in HTML', unique=True, max_length=2000)
	description = models.TextField(verbose_name='Description in BBCode', unique=True, max_length=1000)
	parent = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="children")
	icon = models.ImageField(upload_to='forum_icons', blank=True, null=True)
	enabled_voting = models.BooleanField(choices=VOTING_CHOICES, default=False)
	default_topic_mode = models.PositiveSmallIntegerField(choices=MODE_CHOICES, default=0) # will be this if user has perm to view, else user order
	enabled_topic_modes = ChoiceArrayField(
		models.PositiveSmallIntegerField(choices=MODE_CHOICES, blank=True,),
		default=list
	)
	default_sort_mode = models.PositiveSmallIntegerField(choices=SORT_CHOICES, default=0) # will be this if user has perm to sort, else user order
	enabled_sort_modes = ChoiceArrayField(
		models.PositiveSmallIntegerField(choices=SORT_CHOICES, blank=True,),
		default=list
	)

	order_with_respect_to = 'parent'

	def __str__(self):
		return self.slug

	def get_children(self, order_by="to be implemented"):
		try:
			return self.owns.children.all().order_by('-pub_date')
		except ObjectDoesNotExist:
			return Forum.objects.none()

	def get_absolute_url(self):
		return reverse('forum:view_forum', args=(self.slug,))

	def yield_parents_upwards(self):
		parents = []
		child = self
		try:
			while True:
				yield child.parent.target
				child = child.parent
		except AttributeError:
			pass

	@property
	def latest_topic(self):
		return self.topics.order_by('pub_date')[0]

	@property
	def oldest_topic(self):
		return self.topics.order_by('-pub_date')[0]

	@property
	def top_topic_by_sort_order(self):
		raise NotImplementedError

	@property
	def last_topic_by_sort_order(self):
		raise NotImplementedError

	def get_topics_by_sort_order(self, mode=lambda x : self.default_sort_mode):#not include sticky
		if mode == 2:
			return self.topics.filter(soft_deleted=False).order_by('-stickied').order_by('-pub_date')
		elif mode == 3:
			return self.topics.filter(soft_deleted=False).order_by('-stickied').order_by('-posts__created')
		else:
			raise NotImplementedError

	@property
	def topic_count(self, include_soft_deleted=False):
		if include_soft_deleted:
			return self.topics.all().count()
		else:
			return self.topics.filter(soft_deleted=False).count()

	@property
	def post_count(self, include_soft_deleted=False):
		if include_soft_deleted:
			return Post.objects.filter(topic__forum=self).aggregate(num=Count('id'))["num"]
		else:
			return Post.objects.filter(topic__forum=self, topic__soft_deleted=False, soft_deleted=False).aggregate(num=Count('id'))["num"]

	class Meta(OrderedModel.Meta):
		permissions = (
			("view_forum", "Can view forum"),
			("create_forum_topic", "Can create topics in forum"),
			("delete_forum_topic", "delete_topic"),
			("edit_forum_topic", "edit_topic"),
			("delete_own_forum_topic", "delete_own_topic"),
			("edit_own_forum_topic", "edit_own_topic"),
			("moderate_forum", "Moderate Forum (Moving topics between forums)"),
			("moderate_forum_topic", "Moderate Topics In Forum"),
			("moderate_own_forum_topic", "Moderate own topics in forum"),
			("moderate_own_forum_topic_posts", "Moderate own posts in topics in forum"),
			("view_votes_topic", "Can view exact number of votes for topic"),
			("view_votes_topic_posts", "Can view exact number of votes for topic posts"),
			("up_vote_topic", "Can upvote topics"),
			("down_vote_topic", "Can downvote topics"),
			("up_vote_topic_post", "Can upvote posts"),
			("down_vote_topic_post", "Can downvote posts"),
			("view_topic_as_mode_tree", "Can set tree view mode"),
			("view_topic_as_mode_classic", "Can set classic view mode"),
			("view_topic_as_mode_tree_vote", "Can set tree+vote view mode"),
			("view_topic_as_mode_classic_vote", "Can set classic+vote view mode"),
			("sort_topic_by_hot", "Can sort by hot"),
			("sort_topic_by_recent", "Can sort by recent"),
			("sort_topic_by_votes", "Can sort by votes"),
			("sort_topic_by_old", "Can sort by old"),
		)

class Topic(models.Model):
	MODE_CHOICES = (
		(0, 'forum default'),
		(1, 'classic'),
		(2, 'tree'),
		(3, 'classic+votes'),
		(4, 'tree+votes'),
	)
	title = models.CharField(verbose_name='Title', unique=False, max_length=100)
	slug = AutoSlugField(unique=True, populate_from="title", sep=".")
	pub_date = models.DateTimeField(verbose_name='Date created', default=timezone.now)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='forum_topics_from', verbose_name='From')
	forum = models.ForeignKey(Forum, related_name='topics')
	soft_deleted = models.BooleanField(default=False)
	stickied = models.BooleanField(default=False)
	icon = models.ImageField(upload_to='forum_icons', blank=True, null=True)
#	votes = # foergin key but cache integer
	default_mode_override = models.PositiveSmallIntegerField(choices=MODE_CHOICES, default=0)
	_metadata = JSONField(blank=True, null=True) #ranking data for sort modes

# implement get absolute url with cache and the other thing specific for this funmc + others models too

	def __str__(self):
		return self.slug

	def get_absolute_url(self):
		return reverse('forum:view_topic', args=(self.slug,))

	@property
	def latest_post(self):
		try:
			return self.posts.filter(soft_deleted=False).order_by('created')[0]
		except IndexError:
			return None

	@property
	def oldest_post(self):
		try:
			return self.posts.filter(soft_deleted=False).order_by('-created')[0]
		except IndexError:
			return None

	@property
	def top_post_by_mode_order(self):
		raise NotImplementedError

	@property
	def last_post_by_mode_order(self):
		raise NotImplementedError

	@property
	def yield_all_by_mode_order(self):
		raise NotImplementedError


	@property
	def post_count(self):
		return self.posts.count()

	class Meta:
		permissions = (
			("view_content", "Can view topic content"),

		)


#		oldest = Post.objects.order_by('-pub_date').distinct('topic__id')

class Post(models.Model):
	created = models.DateTimeField(verbose_name='Date created', default=timezone.now)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='forum_posts_from')
	changed_by = models.ForeignKey('auth.User')
	message_html = models.TextField(verbose_name='Message in HTML', unique=True, max_length=50000)
	message = models.TextField(verbose_name='Message in BBCode', unique=True, max_length=40000)
	topic = models.ForeignKey(Topic, related_name='posts', verbose_name='In Topic')
	slug = AutoSlugField(unique=True, populate_from="pk", sep=".")
	soft_deleted = models.BooleanField(default=False)
	_message_metadata = JSONField(default=message_metadata_factory)

	history = HistoricalRecords()

	def __str__(self):
		return self.slug

	def get_absolute_url(self):
		return reverse('forum:view_post', args=(self.slug,))

	def _make_slug(self):
		return "{0}.p".format(self.topic.slug)

	@property
	def _history_user(self):
		return self.changed_by

	@_history_user.setter
	def _history_user(self, value):
		self.changed_by = value

	@property
	def hashtags(self):#are search tags
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



#	def save(self, *args, **kwargs):
#		if not self.id:
#			# Newly created
#			if not self.slug:
#				self = super().save(*args, **kwargs)
#				self.slug = slugify("{0}.{1}".format(self.title, self.id))
#				self.save()