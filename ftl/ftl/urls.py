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
#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path, reverse_lazy
from django.views.generic import RedirectView
from django_registration.backends.activation.views import ActivationView

from ftl import views
from ftl.forms import FTLAuthenticationForm
from ftl.ftl_setup_middleware import SetupState
from ftl.views import PasswordResetAsked, PasswordResetDone

urlpatterns = [
    path('admin/', admin.site.urls),
    # Need to be at the top, otherwise admin url resolve conflict with other urls

    path('', RedirectView.as_view(url=reverse_lazy('home')), name='root'),
    path('setup/', include('setup.urls')),
    path('app/', include('core.urls')),

    path('signup/', views.CreateOrgAndFTLUser.as_view(), name='signup_org_user'),
    path('signup/success/', views.signup_success, name='signup_success'),
    # Disabled until multi users feature is ready
    # path('signup/<slug:org_slug>/', views.CreateFTLUserFormView.as_view(), name='signup_user'),

    path('login/',
         auth_views.LoginView.as_view(authentication_form=FTLAuthenticationForm, redirect_authenticated_user=True),
         kwargs={"ftl_setup_state": SetupState.admin_created}, name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetAsked.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetDone.as_view(), name='password_reset_complete'),

    # Account activation
    path('accounts/activate/complete/', views.AccountActivationSuccess.as_view(),
         name='django_registration_activation_complete'),

    # The activation key can make use of any character from the URL-safe base64 alphabet, plus the colon as a separator.
    url(r'^accounts/activate/(?P<activation_key>[-:\w]+)/$', ActivationView.as_view(),
        name='django_registration_activate'),
]

if settings.DEBUG and settings.DEV_MODE:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.DEV_MODE:
    from ftl import view_local_proxy

    urlpatterns += [
        re_path(r'^local/(?P<url>.*)$', view_local_proxy.LocalProxy.as_view())
    ]
