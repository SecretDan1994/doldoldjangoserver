from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, AppRegistryNotReady
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from skcode import parse_skcode, render_to_html

from steam import SteamID

class _site_settings(object):
	def __getattr__(self, name):
		self.model = apps.get_model("base", "SiteSetting")
		self.__getattr__ = self.__getattr__loaded
		return self.__getattr__(name)

	def __getattr__loaded(self, name):
		value = self.model.get_setting(name)
		return value

site_settings = _site_settings()

class _site_settings_ensure(object):
	def __init__(self):
		self.delayed_execute = []

	def __call__(self, *args, **kwargs):
		try:
			self.model = apps.get_model("base", "SiteSetting")
		except AppRegistryNotReady:
			self.delayed_execute.append((args, kwargs),)
		else:
			self.__call__ = self.__call__loaded
			for args, kwargs in self.delayed_execute:
				self.__call__(*args, **kwargs)
			self.__call__(*args, **kwargs)

	def __call__loaded(self, *args, **kwargs):
		self.model.ensure(*args, **kwargs)

	def on_ready(self):
		self.model = apps.get_model("base", "SiteSetting")
		self.__call__ = self.__call__loaded
		for args, kwargs in self.delayed_execute:
			self.__call__(*args, **kwargs)


site_setting_ensure = _site_settings_ensure()

def get_model_by_steamid(steamid):
	try:
		return apps.get_model("steamauthprovider", "SteamUser").objects.get(steamid64=SteamID(steamid).as_64)
	except ObjectDoesNotExist:
		return False

def message_metadata_factory():
	return {"hashtags":[],"user_mentions":[],"group_mentions":[]}

def get_preferred_name_by_userid(user_id):
	name = cache.get("user-pn-{0}".format(user_id))
	if name == None:
		try:
			steamuser = apps.get_model("steamauthprovider", "SteamUser").objects.get(user__id=user_id)
		except ObjectDoesNotExist:
			name = get_user_model().objects.get(id=user_id).username
		else:
			name = steamuser.get_preferred_name()
		cache.set("user-pn-{0}".format(user_id), name, 5*60)
	return name

def get_preferred_name_by_instance(user):
	name = cache.get("user-pn-{0}".format(user.id))
	if name == None:
		try:
			steamuser = user.steamuser
		except ObjectDoesNotExist:
			name = user.username
		else:
			name = steamuser.get_preferred_name()
		cache.set("user-pn-{0}".format(user.id), name, 5*60)
	return name

def get_page(objects, request, size):
	try:
		return Paginator(objects, size).page(request.GET.get('page', 1))
	except InvalidPage:
		return None

def convert_text_to_html(text, markup="bbcode"):
	if markup == 'bbcode':
		document = parse_skcode(text)
		text = render_to_html(document)
		text = text.replace('\n', '<br>')
		return text
	else:
		raise ValueError('Invalid markup property: {0}'.format(markup))