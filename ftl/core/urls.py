from django.urls import path
from . import views

app_name = 'app'
urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.UserSignupView.as_view(), name='signup'),
]

