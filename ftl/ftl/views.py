from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


def index(request):
    try:
        u = User.objects.get(username='admin')
    except ObjectDoesNotExist:
        context = {'message': 'Please create admin user or launch first migration'}
    else:
        context = {'message': 'TODO Redirect to user signup page'}
    return render(request, 'landing_page.html', context)
