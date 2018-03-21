from .forms import AddSuggestionForm
from .models import SuggestionVote, Suggestion
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.db import transaction

from base.util import get_page, get_preferred_name_by_instance, site_settings

import json


#TODO implement comments, all templates, index
JSON_POST_TUPLE = (-1,1)


@login_required
def add_suggestion(request):
	form_kwargs = {"user": request.user.id}

	if request.method == 'POST':
		form = AddSuggestionForm(request.POST, **form_kwargs)
		if form.is_valid():
			suggestion = form.save()
			form.save_m2m()
			messages.success(request, "Suggestion Saved")
			return HttpResponseRedirect(suggestion.get_absolute_url)
		else:
			raise Exception("Form Not Valid")
	else:
		form = AddSuggestionForm(**form_kwargs)

	context = {
		'form': form,
		'form_url': request.path,
	}
	return render(request, 'suggestions/add.html', context)

def view_suggestion(request, slug=None, object_id=None):
	if slug:
		suggestion = get_object_or_404(Suggestion, slug=slug)
	elif object_id:
		suggestion = get_object_or_404(Suggestion, id=object_id)
	else:
		raise Http404(_("Suggestion does not exist"))

	try:
		if not request.user.is_authenticated():
			raise ObjectDoesNotExist
		vote = request.user.votes_from.get(for_suggestion=suggestion).value
	except ObjectDoesNotExist:
		vote = 0

	context = {
		'suggestion': suggestion,
		'vote_up_active': True if vote == 1 else False,
		'vote_down_active': True if vote == -1 else False,
	}

	return render(request, 'suggestions/view.html', context)

@login_required
def edit_suggestion(request, slug=None, object_id=None):
	raise NotImplementedError("You are in the right place at the wrong time, please come back in the future.")

def index(request):
	suggestions = Suggestion.get_filtered_with_rating({"status__value__in": site_settings.SUGGESTIONS_ARCHIVED_VALUE}, exclude=True).select_related('status').prefetch_related('categories').order_by('-time')

	context = {
		'suggestions_page': get_page(suggestions, request, 25),
	}
	return render(request, 'suggestions/index.html', context)

def filtered_overview(request):
	query_dict = {}
	in_all_cats = request.GET.getlist('all', False)
	categories = request.GET.getlist('c', None)
	status = request.GET.getlist('s', None)

	if categories:
		query_dict["status__value__in"] = status
	if status:
		query_dict["categories__value__in"] = status

	suggestions = Suggestion.get_filtered_with_rating(query_dict)

	if in_all_cats:
		suggestions = suggestions.annotate(num_tags=Count('tags')).filter(num_tags=len(categories))

	suggestions = suggestions.select_related('status').prefetch_related('categories').order_by('-time')

	context = {
		'suggestions_page': get_page(suggestions, request, 25),
	}
	return render(request, 'suggestions/filtered.html', context)	

def post_vote(request):
	if not request.user.is_authenticated(): #has perms?
		response_data = {"ERROR": "No Permission"}
	elif request.method == 'POST':
		for_suggestion = int(request.POST.get('for_suggestion'))
		vote_data = int(request.POST.get('vote_data'))
		if vote_data not in JSON_POST_TUPLE:
			response_data = {"ERROR": "Invalid Post Data"}
		else:
			response_data = {}
			try:
				suggestion = Suggestion.objects.get(id=for_suggestion)
			except ObjectDoesNotExist:
				response_data = {"ERROR": "Invalid Post Data"}
			else:
				with transaction.atomic():
					try:
						vote = SuggestionVote.objects.get(from_user=request.user, for_suggestion=suggestion)
					except ObjectDoesNotExist:
						vote_diffrence = vote_data
						vote = SuggestionVote.objects.create(from_user=request.user, for_suggestion=suggestion, value=vote_data)
					else:
						vote_diffrence = vote_data*-1 if vote.value == vote_data else vote_data*2
						if vote.value == vote_data:
							vote.delete()
						else:
							vote.time=timezone.now()
							vote.value=vote_data
							vote.save()

				response_data['result'] = 'OK'

				response_data['vote_data'] = vote_diffrence
				response_data['for_suggestion'] = for_suggestion
	else:
		response_data = {"ERROR": "No Post Data"}

	return HttpResponse(
		json.dumps(response_data),
		content_type="application/json"
	)

	# how to implement on index: https://realpython.com/blog/python/django-and-ajax-form-submissions/