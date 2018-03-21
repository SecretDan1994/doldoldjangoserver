# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 09:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time')),
                ('title', models.TextField(max_length=100, unique=True, verbose_name='Title')),
                ('message', models.TextField(max_length=40000, unique=True, verbose_name='Message')),
                ('message_html', models.TextField(blank=True, max_length=50000, unique=True, verbose_name='Message HTML')),
            ],
            options={
                'verbose_name': 'Suggestion',
                'verbose_name_plural': 'Suggestions',
                'ordering': ('time', 'status', 'title'),
                'permissions': (('post_suggestion', 'Submit Suggestion'), ('edit_suggestion', 'Edit own Suggestion'), ('post_vote', 'Vote on Suggestions'), ('edit_vote', 'Edit own vote'), ('post_comment', 'Submit Comment'), ('edit_comment', 'Edit own Comment'), ('moderate_suggestion', 'Edit and delete other Suggestion'), ('moderate_comment', 'Edit and delete other comment'), ('devupdate_suggestion', 'Change others suggestion status (for developers)')),
            },
        ),
        migrations.CreateModel(
            name='SuggestionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(max_length=25, verbose_name='Value')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('value',),
            },
        ),
        migrations.CreateModel(
            name='SuggestionComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time')),
                ('body', models.TextField(verbose_name='Body')),
                ('body_html', models.TextField(verbose_name='HTML version')),
                ('for_suggestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='suggestions.Suggestion', verbose_name='To')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestion_comments_from', to=settings.AUTH_USER_MODEL, verbose_name='From')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
        ),
        migrations.CreateModel(
            name='SuggestionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(max_length=25, verbose_name='Value')),
                ('value_html', models.TextField(max_length=250, verbose_name='HTML Value')),
            ],
            options={
                'verbose_name': 'Status',
                'verbose_name_plural': 'Statuses',
                'ordering': ('value',),
            },
        ),
        migrations.CreateModel(
            name='SuggestionVote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.SmallIntegerField(choices=[(-1, 'Down'), (1, 'Up')], verbose_name='Vote Value')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Time')),
                ('for_suggestion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes', to='suggestions.Suggestion', verbose_name='For')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='votes_from', to=settings.AUTH_USER_MODEL, verbose_name='From')),
            ],
            options={
                'verbose_name': 'Vote',
                'verbose_name_plural': 'Votes',
            },
        ),
        migrations.AddField(
            model_name='suggestion',
            name='categories',
            field=models.ManyToManyField(to='suggestions.SuggestionCategory'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='from_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestions_from', to=settings.AUTH_USER_MODEL, verbose_name='From'),
        ),
        migrations.AddField(
            model_name='suggestion',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='suggestions.SuggestionStatus'),
        ),
        migrations.AlterUniqueTogether(
            name='suggestionvote',
            unique_together=set([('from_user', 'for_suggestion')]),
        ),
    ]
