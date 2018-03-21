from django.db import models
from ordered_model.models import OrderedModel
from django.contrib.postgres.fields import JSONField
from simple_history.models import HistoricalRecords
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.core.validators import *
from django.contrib.auth.models import Permission
from base.util import message_metadata_factory, site_setting_ensure
from django.core.exceptions import PermissionDenied
import re

site_setting_ensure("USERSETTINGS_CACHE_TIMEOUT", 0, "How long to cache user settings, 0 is indefinite")


class UserSettingValidator(models.Model):
	MODE_CHOICES = (
		("regex", 'Regex valid if match'),
		("regex-inverse", 'Regex valid if no match'),
		("exact", 'Allows this exact value'),
		("max", 'Max number'),
		("min", 'Min number'),
		("max-len", 'Max length'),
		("min-len", 'Max length'),
		("any", "Allow any value")
	)
	mode = models.CharField(max_length=255, choices=MODE_CHOICES, default="any")
	value = JSONField(null=True, blank=True)
	permission = models.ForeignKey(Permission, null=True, blank=True)
	fail_message = models.CharField(max_length=500, null=True, blank=True)
	hint_message = models.CharField(max_length=500, null=True, blank=True)

	def validate(self, value, user):
		if self.mode == MODE_CHOICES[0][0]:
			return bool(re.search(self.value, value))
		elif self.mode == MODE_CHOICES[1][0]:
			return not bool(re.search(self.value, value))
		elif self.mode == MODE_CHOICES[2][0]:
			return self.value == value
		elif self.mode == MODE_CHOICES[3][0]:
			return self.value >= value
		elif self.mode == MODE_CHOICES[4][0]:
			return self.value <= value
		elif self.mode == MODE_CHOICES[5][0]:
			return self.value >= len(value)
		elif self.mode == MODE_CHOICES[6][0]:
			return self.value <= len(value)
		elif self.mode == MODE_CHOICES[7][0]:
			return True

	def __str__(self):
		return "{0} when user has perm: {1}".format(self.hint_message, self.permission)

	def get_permission_string(self):
		return "{0}.{1}".format(self.permission.content_type.app_label, self.permission.name)

	@classmethod
	def ensure(clas, mode, value=None, permission=None, fail_message=None, hint_message=None):
		validator = clas.objects.get_or_create(mode=mode, value=value, permission=permission, fail_message=fail_message, hint_message=hint_message)
		return validator

class UserSetting(models.Model):
	name = models.CharField(max_length=100, unique=True)
	default_value = JSONField()
	description = models.TextField(max_length=1000, blank=True, null=True)
	userconfig_validation = models.ManyToManyField(UserSettingValidator)

	def __str__(self):
		return self.name

	@property
	def default_value_preview(self):
		return str(self.default_value)[:25]

	def save(self, *args, **kwargs):
		return super().save(*args, **kwargs)

	def get_data_for_user(self, user):
		self.get_user_setting(self.name, user)

	@classmethod
	def get_user_setting(clas, setting, user):
		value = cache.get("usersetting-{0}-{1}".format(setting, user.id))
		if not value:
			try:
				value = UserSettingData.objects.get(for_setting__name=setting, for_user=user).value
			except UserSettingData.DoesNotExist:
				value = clas.objects.get(name=setting).default_value
			cache.set("usersetting-{0}-{1}".format(setting, user.id), value, site_settings.USERSETTINGS_CACHE_TIMEOUT)
		return value

	@classmethod
	def ensure(clas, name, userconfig_validators=None, default=None, description=None):
		if not clas.objects.filter(name=name).exists():
			setting = clas(name=name, default_value=default, description=description)
			if userconfig_validators == None:
				pass
			elif isinstance(userconfig_validators, list) or isinstance(userconfig_validators, tuple):
				setting.userconfig_validation.add(*userconfig_validators)
			else:
				raise TypeError("Argument 'userconfig_validators' must be of type '{}', '{}' or '{}'.".format(type(None), list, tuple))
			setting.save()


class UserSettingData(models.Model):
	value = JSONField()
	for_setting = models.ForeignKey(UserSetting, related_name='data', on_delete=models.CASCADE)
	for_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='settings', on_delete=models.CASCADE)

	class Meta:
		unique_together = ('for_setting', 'for_user',)

	def get(self, setting):
		user = self.for_user
		return UserSetting.get_user_setting(setting, user)

	def set_by_user(self, value, save=True):
		validation_config = self.for_setting.userconfig_validation
		user = self.for_user

		if not validation_config:
			raise PermissionDenied("For setting {0} no validators are configured to allow the user to change it.".format(self.for_setting.name))

		for validator in validation_config:
			if validator.validate(value) and user.has_perm(validator.get_permission_string()):
				self.value = value
				break
		else:
			raise PermissionDenied("The value {0} is not valid for user change by this user for setting {1}.".format(value, self.for_setting.name))

		if save:
			return self.save()

	def save(self, *args, **kwargs):
		rtn = super().save(*args, **kwargs)
		cache.set("usersetting-{0}-{1}".format(self.for_setting.name, self.for_user.id), self.value)
		return rtn

	def __str__(self):
		return "{0} for {1} | {2}".format(self.value, self.for_setting, self.for_user.username)