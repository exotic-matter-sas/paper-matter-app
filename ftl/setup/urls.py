from django.urls import path
from . import views

app_name = 'setup'
urlpatterns = [
    path('step/1/', views.landing_page_step1_view, name='landing_page_step1'),
    path('step/2/', views.LandingPageStep2View.as_view(), name='landing_page_step2'),
    path('success/', views.success, name='success'),
]

