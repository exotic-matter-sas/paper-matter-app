from django.contrib.auth.signals import user_logged_out
from django.contrib import messages
from django.utils.translation import gettext as _


def show_message(sender, user, request, **kwargs):
    # whatever...
    messages.success(request, _('You have been logged out. See you!'), extra_tags='alert alert-success text-center')


user_logged_out.connect(show_message, dispatch_uid='login_page')
