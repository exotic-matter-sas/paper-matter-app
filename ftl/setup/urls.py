from django.urls import path
from . import views

app_name = 'setup'
urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing_page'),
    path('success/', views.success, name='success'),
]

