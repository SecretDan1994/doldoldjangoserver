from django.db import models, transaction
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.util import site_settings, site_setting_ensure

import steamodd, steam, steamauth


steamodd.api.key.set(settings.STEAM_API_KEY)

site_setting_ensure("STEAMAUTH_SIGNUP_REQUIREMENTS", {'max_vac_bans': 0, 'max_game_bans': 0, 'cannot_be_community_ban': True, 'cannot_be_eco_ban': True, 'min_level': 11, 'profile_must_be_setup': True}, "The requirements to get an active account by signing up with a steam profile.")
site_setting_ensure("STEAMAUTH_STEAMUSER_GROUP", 'Steam Users')


class SteamUser(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='steamuser', on_delete=models.SET_NULL, null=True)
	steamid64 = models.CharField(max_length=17, unique=True)
	PREFERRED_NAME_TYPE_CHOICES = (
		(1, 'Steam Name'),
		(2, 'Self Defined Name'),
	)
	preferred_name_type = models.PositiveSmallIntegerField(choices=PREFERRED_NAME_TYPE_CHOICES, default=1)

	def __init__(self, *arg, **kwargs):
		super().__init__(*arg, **kwargs)
		self._steam_user, self._steam_ids, self._steam_bans = cache.get_or_set("steamid{0}".format(self.steamid64), lambda: (steamodd.user.profile(self.steamid64), steam.steamid.SteamID(self.steamid64), steamodd.user.bans(self.steamid64)), 5*60)

	def __str__(self):
		try:
			return "{0} [{1}]".format(self.persona, self.steamid64)
		except Exception:
			return "-- [{0}]".format(self.steamid64)

	def save(self, *args, **kwargs):
		self.refresh_cache()
		if self._state.adding:
			group, created = Group.objects.get_or_create(name=site_settings.STEAMAUTH_STEAMUSER_GROUP)
			self.user.groups.add(group)
		super().save(*args, **kwargs)

	def refresh_cache(self):
		self._steam_user, self._steam_ids, self._steam_bans = (steamodd.user.profile(self.steamid64), steam.steamid.SteamID(self.steamid64), steamodd.user.bans(self.steamid64))
		cache.set("steamid{0}".format(self.steamid64), (self._steam_user, self._steam_ids, self._steam_bans), 5*60)

	@property
	def profile(self):
		return self._steam_user

	@property
	def bans(self):
		return self._steam_bans

	@property
	def ids(self):
		return self._steam_ids

	@property
	def persona(self):
		return self._steam_user.persona

	@property
	def real_name(self):
		return self._steam_user.real_name

	@property
	def preferred_name(self):
		return cache.get_or_set("user-pn-{0}".format(self.user.id), self.get_preferred_name, 5*60)

	def get_preferred_name(self):
		if self.preferred_name_type == 1: 
			return self.persona
		elif self.preferred_name_type == 2: 
			return self.user.username
		else:
			raise NotImplementedError("Preferred name type '{0}' is invalid.".format(self.preferred_name_type))

	@classmethod
	def create_with_user(modelcls, steamid64):
		with transaction.atomic():
			try: 
				steamuser = modelcls.objects.get(steamid64=steamid64)
			except modelcls.DoesNotExist: #nosteamuser
				user = get_user_model().objects.create_user(username="steamid64.{0}".format(steamid64), password=User.objects.make_random_password())
				steamuser = modelcls.objects.create(steamid64=steamid64, user=user) 
			else:
				raise ValueError("SteamUser {0} already exists.".format(steamuser))
		return steamuser

	@classmethod
	def ensure(modelcls, steamid64):
		steamuser, created = modelcls.objects.get_or_create(steamid64=steamid64, defaults={"user":None,})
		return (steamuser, created)

	@classmethod
	def ensure_with_user(modelcls, steamid64):
		created = False
		try:
			steamuser = modelcls.objects.get(steamid64=steamid64)
		except ObjectDoesNotExist:
			steamuser = modelcls.create_with_user(steamid64)
			created = True
		else:
			with transaction.atomic():
				if not steamuser.user:
					user = get_user_model().objects.create_user(username="steamid64.{0}".format(steamid64), password=User.objects.make_random_password())
					steamuser.user=user
					steamuser.save()
					created = True
		return (steamuser, created)


#class SteamUserMetaData(models.Model):
#	steamuser = models.OneToOneField(SteamUser, related_name='metadata', on_delete=models.CASCADE)

#	def __init__(self, *arg, **kwargs):
#		pass

#	def __str__(self):
#		return self.steamid64 + ".meta"

#	__unicode__ = __str__

#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
#def save_user_profile(sender, instance, created, **kwargs):
#	if created:
#		SteamUser.objects.create(user=instance)
#UserCreationForm


class SteamAuthBackend(object):
	def authenticate(self, request_get_data=None):
		try:
			verified_steamid64 = steamauth.GetSteamID64(request_get_data)
		except Exception:
			return None
		else:
			if not verified_steamid64:
				return None

		steamuser, created = SteamUser.ensure_with_user(verified_steamid64)
		authed_user = steamuser.user

		if created:
			fails = self.check_requirements(authed_user)
			if fails:
				authed_user.is_active = False
				authed_user.save()

		return authed_user

	@classmethod
	def check_requirements(cls, user):
		requirements = site_settings.STEAMAUTH_SIGNUP_REQUIREMENTS
		fails = []
		if requirements.get("profile_must_be_setup", False) and not user.steamuser.profile.configured:
			fails.append("profile_must_be_setup")
		if requirements.get("cannot_be_eco_ban", False) and user.steamuser.bans.economy != "none": 
			fails.append("cannot_be_eco_ban")
		if user.steamuser.profile.level < requirements.get("min_level", 0):
			fails.append("min_level")
		if (requirements.get("max_game_bans", None) is not None) and user.steamuser.bans.game_count > requirements.get("max_game_bans", None):
			fails.append("max_game_bans")
		if (requirements.get("max_vac_bans", None) is not None) and user.steamuser.bans.game_count > requirements.get("max_vac_bans", None):
			fails.append("max_vac_bans")
		return fails

	def get_user(self, user_id=None, steamid64=None):
		if user_id != None:
			try:
				steamuser = SteamUser.objects.get(user__pk=user_id)
				return steamuser.user
			except Exception:
				return None
		elif steamid64:
			try:
				steamuser = SteamUser.objects.get(steamid64=steamid64)
				return steamuser.user
			except Exception:
				return None
		else:
			raise ValueError("user_id and steamid64 cannot both be None")