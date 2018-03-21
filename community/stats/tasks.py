from __future__ import absolute_import

from datetime import datetime, timedelta
from django.utils.timezone import utc
from contextlib import suppress

from celery import shared_task
from .models import GameServer, LogTag
from django.core.cache import cache
from channels import Channel, Group
from channels.sessions import channel_session
import json

from django.contrib.auth.models import Permission

from itertools import chain

from django.conf import settings
from steamauthprovider.models import SteamUser
import steamodd, steam
from channels import Channel
from .models import GameServer, LogTag, ServerLog

from .views import SCOREBOARD_GO_BACK_FOR_SEC
from valve.source.a2s import ServerQuerier

import pytz

#todo ensure tags exist on connect
# render scoreboard on snapshot instead of only deleting it?
#@shared_task(ignore_result = True, rate_limit="50/s")
@shared_task(ignore_result = True)
def on_recieve_stats_msg(msg, msg_id, gs_id, reply_channel):
#	print("on_recieve_stats_msg", msg, msg_id, gs_id, reply_channel)
	time = datetime.fromtimestamp(msg["time"]).replace(tzinfo=pytz.UTC)

	kind = msg["kind"]
	data = msg["data"]

	gameserver = GameServer.objects.get(id = gs_id)
	tag = LogTag.objects.get(name=kind)
	
	log = gameserver.logs.create(time=time, data=data, kind="gs-stats", tag=tag)

	if kind == "snapshot":
		cache.delete("stats-scoreboard-gs-{0}".format(gameserver.id))

	Group("scoreboard-live-{0}".format(gs_id)).send({
	 						"text": json.dumps({
	 							"cmd":"gs-stats-liveupdate", 
	 							"payload": {
	 								"time": time.isoformat(),
	 								"data": data,
	 								"tag": tag.name,
	 								"dbid": tag.id,
	 								"pretty_print": log.pretty_print_log,
	 							}
	 						}),
	})

def get_user_permissions(user):
    if user.is_superuser:
        return Permission.objects.all()
    return set(chain(user.user_permissions.all(), Permission.objects.filter(group__user=user)))


@shared_task(ignore_result = True)
def on_gs_user_logon(msg, msg_id, gs_id, reply_channel):
#	print("on_recieve_stats_msg", msg, msg_id, gs_id, reply_channel)
	time = datetime.fromtimestamp(msg["time"]).replace(tzinfo=pytz.UTC)

	recieved_steamid = msg["steamid"]

	steamid64 = steam.steamid.SteamID(recieved_steamid).as_64
	steamuser, created = SteamUser.ensure(steamid64)

	return_data = {}

	if steamuser.user:
		return_data["permissions"] = [x.name for x in get_user_permissions(steamuser.user)]
		return_data["is_registered"] = True
		return_data["is_active"] = steamuser.user.is_active
	else:
		return_data["permissions"] = [] #no permissions because not registered
		return_data["is_registered"] = False
		return_data["is_active"]= False

	return_data["is_new"] = created

	Channel(reply_channel).send(text=json.dumps({"msg_id":msg_id, "rtnkwargs":return_data}))

#create a tast for every steam id to refresh every 5 min / done?

	steamuser = SteamUser.objects.get(id = current_id)
	steam_user, steam_ids = (steamodd.user.profile(steamuser.steamid64), steam.steamid.SteamID(steamuser.steamid64))
	cache.set("steamid{0}".format(self.steamid64), (steam_user, steam_ids), 5*60)
	name = steamuser.get_preferred_name()
	cache.set("user-pn-{0}".format(steamuser.user.id), name, 5*60)

def source_query(ip, port, retry=1):
	while True:
		try:
			return dict(ServerQuerier((ip, port),).info())
		except Exception as exc:
			retry -= 1
			if retry <= 0:
				raise

@shared_task(soft_time_limit = 7, time_limit = 14, ignore_result = True, routing_key='lowpriority.refresh_gs_cache')
def refresh_gs_cache(current_id):
	gameserver = GameServer.objects.get(id=current_id)
	try:
		snapshot = gameserver.logs.filter(tag__name='snapshot').order_by('-time')[0]
	except IndexError:
		try:
			query_info = source_query(gameserver.ip, gameserver.port, retry=2)
		except Exception:
			cache.set("stats-basic-gs-{0}".format(current_id), ({"status":GameServer.QueryType.Offline, "map":None, "hostname":None, "slots":(None, None),}, datetime.utcnow().replace(tzinfo=utc)), 4*59)
		else:
			cache.set("stats-basic-gs-{0}".format(current_id), ({"status":GameServer.QueryType.SourceQuery, "map":query_info["map"], "hostname":query_info["server_name"], "slots":(query_info["player_count"], query_info["max_players"]),}, datetime.utcnow().replace(tzinfo=utc)), 4*59)

		return

	scoreboard = snapshot.data
	last_cache_at = snapshot.time

	for team in gameserver.game.teams.all():
		try:
			if not scoreboard["teams"][str(team.identifier)]:
				scoreboard["teams"][str(team.identifier)] = {"name":team.name,}
		except KeyError:
			scoreboard["teams"][str(team.identifier)] = {"name":team.name,}

	selected_events = gameserver.logs.filter(time__gt=last_cache_at).select_related("tag").order_by('time')
	generation_time = gameserver.logs.all().order_by('-time')[0].time

	time_threshold = datetime.now() - timedelta(seconds=SCOREBOARD_GO_BACK_FOR_SEC)
	selected_logs = gameserver.logs.filter(time__gt=time_threshold).select_related("tag").order_by('time')


	for log in selected_events:

		try:

			if log.tag.name == 'player_death':
				scoreboard["players"][log.data["steamid"]]["alive"] = False
				with suppress(KeyError):
					scoreboard["players"][log.data["attacker"]]["kills"] += 1
				scoreboard["players"][log.data["steamid"]]["deaths"] += 1

			elif log.tag.name == 'player_team':
				scoreboard["players"][log.data["steamid"]]["team"] = log.data["team"]

			elif log.tag.name == 'round_end':
				scoreboard["teams"][str(log.data["winner"])]["score"] += 1

			elif log.tag.name == 'player_spawn':
				scoreboard["players"][log.data["steamid"]]["alive"] = True

			elif log.tag.name == 'player_connect':
				scoreboard["players"][log.data["steamid"]] = {"alive":False, "active":False, "tag":False, "deaths":0, "kills":0, "ip":log.data["ip"], "team":0, "name":log.data["name"], "mvp":0}

			elif log.tag.name == 'player_changename':
				scoreboard["players"][log.data["steamid"]]["name"] = log.data["newname"]

			elif log.tag.name == 'round_mvp':
				scoreboard["players"][log.data["steamid"]]["mvp"] += 1

			elif log.tag.name == 'player_disconnect':
				del scoreboard["players"][log.data["steamid"]]

			elif log.tag.name == "game_newmap":
				scoreboard["map"] = log.data["mapname"]

				for player in scoreboard["players"].keys():
					scoreboard["players"][player]["active"] = False

			elif log.tag.name == "player_avenged_teammate":
				pass #toimplement

			elif log.tag.name == "player_activate": # disconbnect can happen after connect on retry
				scoreboard["players"][log.data["steamid"]]["active"] = True 
	#            try:
	#                scoreboard["players"][log.data["steamid"]]["active"] = True 
	#            except KeyError:
	#                connect_event = gameserver.logs.filter(tag__name='player_connect', time__lt=generation_time).order_by('-time')[0]
	#                scoreboard["players"][log.data["steamid"]] = {"alive":False, "active":True, "tag":False, "deaths":0, "kills":0, "ip":connect_event.data["ip"], "team":0, "name":connect_event.data["name"], "mvp":0}

			elif log.tag.name == "round_start":
				pass #toimplement - we dont have to do anything?

			elif log.tag.name == "game_end":
				for player, data in scoreboard["players"].items():
					data["kills"] = 0
					data["deaths"] = 0
					data["mvp"] = 0
					scoreboard["players"][player] = data

				for team in scoreboard["teams"].keys():#.items():
	#                data["player_count"] = 0
	 #                data["alive_count"] = 0
	#                data["score"] = 0
					scoreboard["teams"][team]["score"] = 0

				scoreboard["round_count"] = 0

			elif log.tag.name == "game_start":
				for player, data in scoreboard["players"].items():
					data["kills"] = 0
					data["deaths"] = 0
					data["mvp"] = 0
					scoreboard["players"][player] = data

				for team in scoreboard["teams"].keys():#.items():
	#                data["player_count"] = 0
	 #                data["alive_count"] = 0
	#                data["score"] = 0
					scoreboard["teams"][team]["score"] = 0

				scoreboard["round_count"] = 0

		except Exception:
			import sys
			exc_info = sys.exc_info()
			raise Exception("{} {} - {}".format(log.id, log.tag, exc_info))

	scoreboard["round_count"] = scoreboard["teams"]["2"]["score"] + scoreboard["teams"]["3"]["score"] + 1
	scoreboard["player_count"] = len(scoreboard["players"])

# handle botcount
# add logic to only add when activate backkquerying player_connect for more info

	cache.set("stats-basic-gs-{0}".format(current_id), ({"status":GameServer.QueryType.LiveScoreboard, "map":scoreboard["map"], "hostname":scoreboard["hostname"], "slots":(scoreboard["player_count"], scoreboard["slots"]),}, datetime.utcnow().replace(tzinfo=utc)), 4*59)
	cache.set("stats-scoreboard-gs-{0}".format(current_id), (scoreboard, generation_time))

@shared_task(rate_limit = "1/m", ignore_result=True)
def gs_cache_checker():
	try:
		gameservers = GameServer.objects.all()
		for gameserver in gameservers:
			refresh_gs_cache.apply_async((gameserver.id,))
	except:
		raise
#	finally:
#		gs_cache_checker.apply_async(countdown=2*60)