from django.views.generic import CreateView
from django.shortcuts import render
from .models import FTLUser


class UserSignupView(CreateView):
    model = FTLUser
    fields = ('ftl_user',)
    template_name = 'core/signup.html'


def login(request):
    return render(request, 'core/login.html')
