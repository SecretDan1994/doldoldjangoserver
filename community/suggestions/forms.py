from .models import Suggestion, SuggestionStatus

from django import forms

from base.util import site_setting_ensure, site_settings
from base.models import SiteSetting#, SuggestionCategory
from django.contrib.auth import get_user_model





# Create the form class.
class AddSuggestionForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super().__init__(*args, **kwargs)

	def save(self, *args, **kwargs):
		x = super().save(commit=False)
		x.from_user = get_user_model().objects.get(id=self.user)
		x.status = SuggestionStatus.objects.get(value=site_settings.SUGGESTIONS_DEFAULT_VALUE)
		x.save()
		return x

	class Meta:
		model = Suggestion
		fields = ('title', 'message', 'categories')


# usage: form = AddSuggestionForm(user=request.user)