from django.shortcuts import render

# Create your views here.

def homepage(request):
	context = {
		'Test': 1,
	}

	return render(request, 'base/homepage.html', context)