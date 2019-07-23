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
from django.urls import path, include, re_path, reverse_lazy
from django.views.generic import RedirectView
from django.utils.translation import gettext_lazy as _

from ftl import views, view_local_proxy
from ftl.ftl_setup_middleware import SetupState
from ftl.views import SetMessageAndRedirectView
from ftl.views_auth import LoginViewFTL

urlpatterns = [
    path('admin/', admin.site.urls),
    # Need to be at the top, otherwise admin url resolve conflict with other urls

    path('', RedirectView.as_view(url=reverse_lazy('home')), name='root'),
    path('setup/', include('setup.urls')),
    path('app/', include('core.urls')),

    path('signup/<slug:org_slug>/', views.CreateFTLUserFormView.as_view(), name='signup'),
    path('signup/<slug:org_slug>/success/', views.signup_success, name='signup_success'),

    path('login/', LoginViewFTL.as_view(redirect_authenticated_user=True),
         kwargs={"ftl_setup_state": SetupState.admin_created}, name='login'),
    path('logout/', auth_views.logout_then_login, name='logout'),

    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',
         SetMessageAndRedirectView.as_view(
             url=reverse_lazy('login'),
             message=_('We’ve emailed you instructions for setting your password, if an account exists with the email '
                       'you entered. You should receive them shortly (check your spam folder if that\'s not the case).')
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/',
         SetMessageAndRedirectView.as_view(
             url=reverse_lazy('login'),
             message=_('Your password has been set. You may go ahead and log in now.')
         ),
         name='password_reset_complete'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

if settings.DEV_MODE:
    urlpatterns += [
        re_path(r'^local/(?P<url>.*)$', view_local_proxy.LocalProxy.as_view())
    ]
