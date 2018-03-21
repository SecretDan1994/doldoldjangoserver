from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.urls import reverse # v10

from base.util import convert_text_to_html, site_settings,  site_setting_ensure

site_setting_ensure("MARKUP", "bbcode", "Markup used for user content")
site_setting_ensure("SUGGESTIONS_DEFAULT_VALUE", "New", "Default Status for suggestions.")
site_setting_ensure("SUGGESTIONS_ARCHIVED_VALUE", ["Completed","Rejected"], "Satuses that count as archived.")

class SuggestionCategory(models.Model):
	value = models.TextField(_('Value'), max_length=25)

	class Meta:
		ordering = ('value',)
		verbose_name = "Category"
		verbose_name_plural = "Categories"

	def __str__(self):
		return self.value

	__unicode__ = __str__

class SuggestionStatus(models.Model):
	value = models.TextField(_('Value'), max_length=25)
	value_html = models.TextField(_('HTML Value'), max_length=250)

	class Meta:
		ordering = ('value',)
		verbose_name = "Status"
		verbose_name_plural = "Statuses"

	def __str__(self):
		return self.value

	__unicode__ = __str__

class Suggestion(models.Model):
	slug = models.SlugField(unique=True, blank=True)
	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='suggestions_from', verbose_name=_('From'))
	time = models.DateTimeField(_('Time'), default=timezone.now)
	title = models.CharField(_('Title'), unique=True, max_length=100)
	message = models.TextField(_('Message'), unique=True, max_length=40000)
	message_html = models.TextField(_('Message HTML'), unique=True, max_length=50000, blank=True)
	status = models.ForeignKey(SuggestionStatus)
	categories = models.ManyToManyField(SuggestionCategory)

	@property
	def get_rating(self):
		return self.votes.all().aggregate(models.Sum('value'))['value__sum']

	@classmethod
	def get_all_with_rating(self):
		return Suggestion.objects.all().annotate(rating=models.Sum('votes__value'))

	@classmethod
	def get_filtered_with_rating(self, filter_args, exclude=False):
		if exclude:
			return Suggestion.objects.exclude(**filter_args).annotate(rating=models.Sum('votes__value'))
		else:
			return Suggestion.objects.filter(**filter_args).annotate(rating=models.Sum('votes__value'))

	@cached_property
	def get_absolute_url(self):
		return reverse('suggestions:view_suggestion_slug', kwargs={'slug': self.slug})

	def save(self, *args, **kwargs):
		if not self.id:
			# Newly created
			if not self.slug:
				self.slug = slugify(self.title)

		if self.message != self.__original_message:
			self.message_html = convert_text_to_html(self.message, site_settings.MARKUP)
#			if forum_settings.SMILES_SUPPORT and self.from_user.forum_profile.show_smilies:
#				self.message_html = smiles(self.message_html)

		super().save(*args, **kwargs)
		self.__original_message = self.message

	class Meta:
		ordering = ('time', "status", "title")
		verbose_name = _('Suggestion')
		verbose_name_plural = _('Suggestions')
		permissions = (
			('post_suggestion', 'Submit Suggestion'),
			('edit_suggestion', 'Edit own Suggestion'),
			('post_vote', 'Vote on Suggestions'),
			('edit_vote', 'Edit own vote'),
			('post_comment', 'Submit Comment'),
			('edit_comment', 'Edit own Comment'),
			('moderate_suggestion', 'Edit and delete other Suggestion'),
			('moderate_comment', 'Edit and delete other comment'),
			('devupdate_suggestion', 'Change others suggestion status (for developers)'),
		)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__original_message = self.message

	def __str__(self):
		return self.slug

	__unicode__ = __str__


class SuggestionComment(models.Model):
	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='suggestion_comments_from', verbose_name=_('From'))
	for_suggestion = models.ForeignKey(Suggestion, related_name='comments', verbose_name=_('To'))
	time = models.DateTimeField(_('Time'), default=timezone.now)
	body = models.TextField(_('Body'))
	body_html = models.TextField(_('HTML version'))

	def save(self, force_insert=False, force_update=False, *args, **kwargs):
		if self.body != self.__original_body:
			self.body_html = convert_text_to_html(self.body, site_settings.MARKUP)
#			if forum_settings.SMILES_SUPPORT and self.from_user.forum_profile.show_smilies:
#				self.body_html = smiles(self.body_html)

		super().save(force_insert, force_update, *args, **kwargs)
		self.__original_body = self.body

	class Meta:
		verbose_name = "Comment"
		verbose_name_plural = "Comments"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__original_body = self.body

	def __str__(self):
		return "SuggestionComment.{0}".format(self.id)

	__unicode__ = __str__


class SuggestionVote(models.Model):
	VALUE_CHOICES = (
		(-1, 'Down'),
		(1, 'Up'),	)
	from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='votes_from', verbose_name=_('From'))
	for_suggestion = models.ForeignKey(Suggestion, related_name='votes', verbose_name=_('For'))
	value = models.SmallIntegerField(verbose_name=_('Vote Value'), choices=VALUE_CHOICES)
	time = models.DateTimeField(_('Time'), default=timezone.now)

	class Meta:
		verbose_name = "Vote"
		verbose_name_plural = "Votes"
		unique_together = (('from_user', 'for_suggestion'),)

	def __str__(self):
		return "SuggestionVote.{0}".format(self.id)

	__unicode__ = __str__
