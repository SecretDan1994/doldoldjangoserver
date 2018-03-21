from django.conf.urls import include
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='server-list'),
    url(r'^(?P<gs_id>[0-9]+)/stats$', views.serverstats, name='server-scoreboard'),
]