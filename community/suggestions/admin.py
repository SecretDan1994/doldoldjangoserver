from django.contrib import admin
from . import models


admin.site.register(models.Suggestion)
admin.site.register(models.SuggestionCategory)
admin.site.register(models.SuggestionStatus)
admin.site.register(models.SuggestionVote)

#Not Implemented: SuggestionComment
