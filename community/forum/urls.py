from django.conf.urls import include, url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^category/(?P<slug>[-\w]+)/$', views.view_category, name='view_category'),
    url(r'^forum/(?P<slug>[-\w]+)/$', views.view_forum, name='view_forum'),
    url(r'^topic/(?P<slug>[-\w]+)/$', views.view_topic, name='view_topic'),
    url(r'^post/(?P<slug>[-\w]+)/$', views.view_post, name='view_post'),
]