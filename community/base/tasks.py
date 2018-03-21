from __future__ import absolute_import

from datetime import datetime
from django.utils.timezone import utc

from celery import shared_task
from steamauthprovider.models import SteamUser
from django.core.cache import cache
from channels.sessions import channel_session
import json

import pytz

import steamodd, steam


#create a tast for every steam id to refresh every 5 min
@shared_task(soft_time_limit = 4, time_limit = 10, ignore_result = True, routing_key='lowpriority.refresh_steam_cache')
def refresh_steam_cache(current_id):
	steamuser = SteamUser.objects.get(id = current_id)
	steamuser.refresh_cache()
	name = steamuser.get_preferred_name()
	cache.set("user-pn-{0}".format(steamuser.user.id), name, 5*60)


@shared_task(rate_limit = "1/m", ignore_result=True)
def steam_cache_checker():
	try:
		steamusers = SteamUser.objects.all()
		for steamuser in steamusers:
			refresh_steam_cache.apply_async((steamuser.id,))
	except:
		raise
#	finally:
#		steam_cache_checker.apply_async(countdown=5*60)


#constantly run throught every steam id to refresh
#@shared_task(soft_time_limit = 4, time_limit = 10, ignore_result = True, rate_limit = "55/m")
#def refresh_steam_cache_m2(current_id):
#	try:
#		steamuser = SteamUser.objects.get(id = current_id)
#		steam_user, steam_ids = (steamodd.user.profile(steamuser.steamid64), steam.steamid.SteamID(steamuser.steamid64))
#		cache.set("steamid{0}".format(self.steamid64), (steam_user, steam_ids), 5*60)
#		name = steamuser.get_preferred_name()
#		cache.set("user-pn-{0}".format(steamuser.user.id), name, 5*60)
#	except SoftTimeLimitExceeded:
#		next_id = current_id
#	except Exception:
#		next_id = SteamUser.objects.filter(id__gt = current_id)[0].id
#	else:
#		next_id = SteamUser.objects.filter(id__gt = current_id)[0].id
#	finally:
#		run_again = datetime.now()
#		refresh_steam_cache.apply_async((next_id,), eta=run_again)