from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'login/', views.login, name='steamlogin'),
	url(r'logout/', views.logout, name='steamlogout'),
	url(r'process/', views.loginprocess, name='steamloginprocess'),
]