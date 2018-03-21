from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import GameServer, LogTag, ServerLog
from contextlib import suppress
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.utils.timezone import utc
import operator

from datetime import datetime, timedelta

from collections import OrderedDict

from pprint import pformat

from django.shortcuts import render_to_response
from django.template import RequestContext

SCOREBOARD_GO_BACK_FOR_SEC = 60*5



def index(request):
	all_gameservers = GameServer.objects.all()

	context = {
		'all_gameservers':all_gameservers
	}
	return render(request, 'stats/index.html' , context)

# force cache deletion when admin is used
# delete cache on new snapshot

# no longer custom round start but snapshot, update this (add round start etc)

# todo fix clantag not working

#todo base.utils.get_model_by_steamid.preferred_name #then also cache this fgor steamid only accounts (already did this?)

def serverstats(request, gs_id):

	with transaction.atomic():

		if gs_id:
			gameserver = get_object_or_404(GameServer, id=gs_id)
		else:
			raise Http404("GameServer does not exist")

		cached_data = cache.get("stats-scoreboard-gs-{0}".format(gs_id))

		if cached_data:
			scoreboard, last_cache_at = cached_data

		else:
			try:
				snapshot = gameserver.logs.filter(tag__name='snapshot').order_by('-time')[0]
			except IndexError: 
				raise Http404("Scoreboard for GameServer does not exist")
			scoreboard = snapshot.data
			last_cache_at = snapshot.time

#            scoreboard["logs"] = []

			# make this instead an optitional override also per server
			for team in gameserver.game.teams.all():
				try:
					if not scoreboard["teams"][str(team.identifier)]:
						scoreboard["teams"][str(team.identifier)] = {"name":team.name,}
				except KeyError:
					scoreboard["teams"][str(team.identifier)] = {"name":team.name,}

		selected_events = gameserver.logs.filter(time__gt=last_cache_at).select_related("tag").order_by('time')
		generation_time = gameserver.logs.all().order_by('-time')[0].time

		# cache printed logs for every permission combination                                                     V^ combine thse 2 queries?

		time_threshold = datetime.now() - timedelta(seconds=SCOREBOARD_GO_BACK_FOR_SEC)
		selected_logs = gameserver.logs.filter(time__gt=time_threshold).select_related("tag").order_by('time')


	for log in selected_events:

#        scoreboard["logs"].insert(0, log.pretty_print_log)
		try:
 
			if log.tag.name == 'player_death':
				scoreboard["players"][log.data["steamid"]]["alive"] = False
				with suppress(KeyError):
					scoreboard["players"][log.data["attacker"]]["kills"] += 1
				scoreboard["players"][log.data["steamid"]]["deaths"] += 1

			elif log.tag.name == 'player_team':
#				scoreboard["players"][log.data["steamid"]]["team"] = log.data["team"]
				try:
					scoreboard["players"][log.data["steamid"]]["team"] = log.data["team"]
				except KeyError:
					pass

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
				try: # when conn refudes can discon but not conn
					del scoreboard["players"][log.data["steamid"]]
				except KeyError:
					pass

			elif log.tag.name == "game_newmap":
				scoreboard["map"] = log.data["mapname"]

				for player in scoreboard["players"].keys():
					scoreboard["players"][player]["active"] = False

			elif log.tag.name == "player_avenged_teammate":
				pass #toimplement

			elif log.tag.name == "player_activate": # disconbnect can happen after connect on retry
#				scoreboard["players"][log.data["steamid"]]["active"] = True 
				try:
					scoreboard["players"][log.data["steamid"]]["active"] = True 
				except KeyError:
					connect_event = gameserver.logs.filter(tag__name='player_connect', time__lt=generation_time).order_by('-time')[0]
					scoreboard["players"][log.data["steamid"]] = {"alive":False, "active":True, "tag":False, "deaths":0, "kills":0, "ip":connect_event.data["ip"], "team":0, "name":connect_event.data["name"], "mvp":0}

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

		except KeyError:
			import sys
			exc_info = sys.exc_info()
			print("Player not in scoreboard - {} / {} - {} - {}".format(log.id, log.tag, log.data, exc_info))
			#
			#request snapshot here
			#
			#Exception("{} {} - {}".format(log.id, log.tag, exc_info))

# handle botcount
# add logic to only add when activate backkquerying player_connect for more info

	cache.set("stats-scoreboard-gs-{0}".format(gs_id), (scoreboard, generation_time))


	scoreboard["logs"] = []

	for log in selected_logs:
		scoreboard["logs"].append(log.pretty_print_log) # log.pretty_print_log : maybe doesnt optimise select related because goes to model?
		# implement permissions for log types

	# maybe  erify snapshot with prev data to dedtermine issues?

	# make round count be calculated from events instead?
	# dont hardcode team 2/3 have something that dynamically selects embattled teams
	scoreboard["round_count"] = scoreboard["teams"]["2"]["score"] + scoreboard["teams"]["3"]["score"] + 1
	scoreboard["player_count"] = len(scoreboard["players"])

	cache.set("stats-basic-gs-{0}".format(gs_id), ({"status":GameServer.QueryType.LiveScoreboard, "map":scoreboard["map"], "hostname":scoreboard["hostname"], "slots":(scoreboard["player_count"], scoreboard["slots"]),}, datetime.utcnow().replace(tzinfo=utc)), 4*59)

	for team in scoreboard["teams"].keys():
		scoreboard["teams"][team]["player_count"] = 0
		scoreboard["teams"][team]["alive_count"] = 0

	for player, data in scoreboard["players"].items():
		try:
			kd = data["kills"]/data["deaths"]
		except ZeroDivisionError:
			kd = data["kills"]
		scoreboard["players"][player]["kd"] = '{0:.2f}'.format(kd)

		if data["alive"]:
			scoreboard["teams"][str(data["team"])]["alive_count"] += 1
		scoreboard["teams"][str(data["team"])]["player_count"] += 1

	scoreboard["players"] = OrderedDict(sorted(scoreboard["players"].items(), key=lambda x: x[1]['kills'], reverse=True))

	context = {
		'scoreboard':scoreboard,
		'gameserver':gameserver,

		'scoreboard_gen_time':generation_time,
		'specteams':(1,0), # instead per game / server intoduce spec teams and active teams
	}
	return render(request, 'stats/serverstats.html' , context)


#def handler404(request):
#    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
#    response.status_code = 404
#
#    return response


#def handler500(request):
#    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
#    response.status_code = 500

#    return response