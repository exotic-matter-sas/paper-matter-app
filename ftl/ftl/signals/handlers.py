from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.utils.translation import gettext as _


def show_message(request, **kwargs):
    if 'auto' in request.GET:
        messages.warning(request, _('Your session has expired or have been invalidated. Please log back in.'))
    else:
        messages.success(request, _('You have been logged out. See you!'))


user_logged_out.connect(show_message, dispatch_uid='login_page')
