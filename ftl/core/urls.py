from django.urls import path

from . import views

app_name = 'app'
urlpatterns = [
    path('login/', views.login_hub, name='login_hub'),
    # path('<str:org_slug>/login/', views.login, name='login'),
    # path('<str:org_slug>/signup/', views.signup, name='signup'),
    # path('<str:org_slug>/signup/success', views.signup_success, name='signup_success'),

]
