from django.db import models
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.html import conditional_escape
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property
from django.urls import reverse # v10
from django.contrib.postgres.fields import JSONField, ArrayField
from simple_history.models import HistoricalRecords

from base.util import convert_text_to_html, site_settings,  site_setting_ensure
from steamauthprovider.models import SteamUser

site_setting_ensure("MARKUP", "bbcode", "Markup used for user content")
site_setting_ensure("SUGGESTIONS_DEFAULT_VALUE", "New", "Default Status for suggestions.")

class PunishmentKind(models.Model):
	name = models.CharField(max_length=255)
	_pretty_name = models.CharField(max_length=500, null=True, blank=True)

	@property
	def pretty_name(self):
		return self._pretty_name or self.name

	@pretty_name.setter
	def pretty_name(self, value):
		self._pretty_name = value

	def __str__(self):
		return self.pretty_name


class Punishment(models.Model): # historic field
	invoked_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='issued_punishments', verbose_name=_('Invoker'))
	invoked_at = models.DateTimeField(default=timezone.now, verbose_name=_('Invokation time'))
	duration = models.DurationField(blank=True, null=True)
	_end_time = models.DateTimeField(default=timezone.now)
	target = models.ForeignKey(SteamUser, related_name='punishments') # changfe to steam id
	message = models.TextField(max_length=4000)
	data = JSONField()
	kind = models.ManyToManyField(PunishmentKind)
	STATUS_CHOICES = (
		(1, 'Active'),
		(2, 'Revoked'),
		(0, 'Deleted'),
	)
	status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
	changed_by = models.ForeignKey(settings.AUTH_USER_MODEL)
	changed_at = models.DateTimeField(default=timezone.now)
	history = HistoricalRecords()

	@property
	def _history_user(self):
		return self.changed_by

	@_history_user.setter
	def _history_user(self, value):
		self.changed_by = value

	@cached_property
	def in_effect(self):
		return True if self.status == 1 and self.end_time >= timezone.now() else False

	def end_time(self):
		return self._end_time

	@classmethod
	def get_in_effect_for_target(clas, target, kinds):
		return clas.objects.filter(kind__in=kinds, status__eq=1, _end_time__gte=timezone.now(), target=target)

	def revoke(self, action_invoker, message=False):
		self.changed_by = action_invoker
		self.changed_at = timezone.now
		self.status = 2
		if message: 
			self.message = message
		self.save()

	def soft_delete(self, action_invoker):
		self.changed_by = action_invoker
		self.changed_at = timezone.now
		self.status = 0
		self.save()

	def change_duration(self, action_invoker):
		self.changed_by = action_invoker
		self.changed_at = timezone.now
		self.status = 0
		self.save()

	def save(self, *args, **kwargs):
		self._end_time = self.invoked_at + self.duration
		return super().save(*args, **kwargs)

	class Meta:
		ordering = ('invoked_at', "status", "kind")
		permissions = (
#			('handle_kind1_punishment', 'Invoke'), so maybe make these manyto many fields
#			('handle_kind2_punishment', 'Invoke'),
#			('handle_kind3_punishment', 'Invoke'),
#			('handle_kind4_punishment', 'Invoke'),
#			('handle_kind5_punishment', 'Invoke'),
			('invoke_punishment', 'Invoke'),
			('revoke_punishment', 'Revoke'),
			('soft_delete_punishment', 'Delete'),
			('change_kind_punishment', 'Change Kind'),
		)

	def __str__(self):
		return "{0} {1} for {2}, {3} {4}".format(status, kind, target.preferred_name, "in effect until" if self.in_effect else "ended", self.end_time)

	__unicode__ = __str__