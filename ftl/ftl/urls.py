"""ftl URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from ftl.views_auth import PasswordResetViewFTL, PasswordChangeViewFTL, PasswordResetConfirmViewFTL
from . import views

urlpatterns = [
    path('app/', include('core.urls'), name='app'),
    path('app/<slug:org_slug>/', include([
        path('login/', auth_views.LoginView.as_view(), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),

        path('password_change/', PasswordChangeViewFTL.as_view(), name='password_change'),
        path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

        path('password_reset/', PasswordResetViewFTL.as_view(), name='password_reset'),
        path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
        path('reset/<uidb64>/<token>/', PasswordResetConfirmViewFTL.as_view(), name='password_reset_confirm'),
        path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    ])),
    path('setup/', include('setup.urls')),
    path('admin/', admin.site.urls),
    path('', views.index),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
