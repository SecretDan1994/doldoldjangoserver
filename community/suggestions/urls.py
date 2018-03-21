from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^add/', views.add_suggestion, name='add_suggestion'),
	url(r'^filtered/$', views.filtered_overview, name='filtered_overview'),  
	url(r'^view/(?P<object_id>\d+)/$', views.view_suggestion, name='view_suggestion_id'),
	url(r'^view/(?P<slug>[-\w]+)/$', views.view_suggestion, name='view_suggestion_slug'),
	url(r'^edit/(?P<object_id>\d+)/$', views.edit_suggestion, name='edit_suggestion_id'),
	url(r'^edit/(?P<slug>[-\w]+)/$', views.edit_suggestion, name='edit_suggestion_slug'),
	url(r'^post_vote/', views.post_vote, name='post_vote'),
]
