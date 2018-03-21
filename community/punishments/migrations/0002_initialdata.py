# -*- coding: utf-8 -*-
from django.db import migrations

def provide_initial_data(apps, schema_editor):
	kind_choices = (
		(0, 'AllBan'),
		(1, 'GameServerBan'),
		(2, 'GameTeamBan'),
		(4, 'TeamSpeakBan'),
		(5, 'SiteBan'),
	)
	PunishmentKind = apps.get_model('punishments', 'PunishmentKind')
	for x,name in kind_choices:
		PunishmentKind.objects.get_or_create(id=x, defaults={"name": name})

class Migration(migrations.Migration):

	dependencies = [
		('punishments', '0001_initial'),
	]

	operations = [
		migrations.RunPython(provide_initial_data),
	]