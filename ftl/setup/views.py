from django.shortcuts import render


def index(request):
    return render(request, 'setup/landing_page.html')
