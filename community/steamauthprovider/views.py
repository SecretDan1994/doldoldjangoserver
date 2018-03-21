from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.core.cache import cache

from django.core.urlresolvers import reverse, NoReverseMatch
#from djangobb_forum.util import absolute_url
from django.http import HttpResponseRedirect
#import djangobb_forum

import steamauth

# /login
def login(request):
    try:
        next_page = request.GET['next']
        next_page = reverse(next_page)
    except KeyError:
        next_page = reverse('home')
    except NoReverseMatch:
        pass

    request.session['login-redirect'] = next_page

    return steamauth.RedirectToSteamSignIn(reverse(loginprocess))

# /logout
def logout(request):
    auth_logout(request)
    messages.success(request, 'Logout Successful')

    try:
        next_page = request.GET['next']
        next_page = reverse(next_page)
    except KeyError:
        next_page = reverse('home')
    except NoReverseMatch:
        pass

    return HttpResponseRedirect(next_page,) #djangobb_forum.views.index(request)

# /process
def loginprocess(request):
    user = authenticate(request_get_data=request.GET)
    if user is None:
        messages.error(request, "Could not log into Steam account.")
    else:
        auth_login(request, user)
        messages.success(request, "Logged into Steam account {0}!".format(user.steamuser.preferred_name))

    try:
        next_page = request.session['login-redirect']
    except KeyError:
        next_page = reverse('home')
    else:
        del request.session['login-redirect']

    return HttpResponseRedirect(next_page,) # absolute_url(
#    return djangobb_forum.views.index(request)

"""

from django.contrib.auth.models import User
get u model.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

"""