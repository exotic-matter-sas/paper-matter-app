from django.core.exceptions import MiddlewareNotUsed
from django.shortcuts import redirect

from core.models import FTLOrg, FTLUser


class SetupState:
    none = 0
    first_org_created = 1
    admin_created = 2


def _redirect_to_setup_step_to_complete(first_org_state, admin_state):
    """Logic to redirect user to appropriate view if required setup state isn't meet"""
    if admin_state:
        return redirect('login')
    else:
        if first_org_state:
            return redirect('setup:create_admin')
        else:
            return redirect('setup:create_first_org')


class FTLSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        if self.first_org_state and self.admin_state:
            raise MiddlewareNotUsed()  # automatic disable when ftl-app is already setup

    @property
    def first_org_state(self):
        return FTLOrg.objects.count() > 0

    @property
    def admin_state(self):
        return FTLUser.objects.filter(is_staff=True).count() > 0

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Put a session flag to indicate that the ftp_setup_middleware is enabled on the current django instance.
        # The setup views will only allow setup if the following flag is present.
        # As such, when the setup is completed, the middleware will not load and the setup views will not have the flag
        # and will denied access to setup views.
        request.session['ftl_setup_middleware'] = True

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if 'ftl_setup_state' in view_kwargs:
            state_error = True
            none_state = not (self.first_org_state or self.admin_state)
            ftl_setup_state_ = view_kwargs['ftl_setup_state']

            if ftl_setup_state_ == SetupState.none:
                if none_state:
                    state_error = False
            elif ftl_setup_state_ == SetupState.first_org_created:
                if self.first_org_state and not self.admin_state:
                    state_error = False
            elif ftl_setup_state_ == SetupState.admin_created:
                if self.first_org_state and self.admin_state:
                    state_error = False
            else:
                raise ValueError(f'excepted_setup_state is not valid, accepted value are:'
                                 f'{[attr for attr in dir(SetupState) if not attr.startswith("_")]}')

            if state_error:
                return _redirect_to_setup_step_to_complete(self.first_org_state, self.admin_state)
            else:
                return None
        else:
            # No key, don't check for setup
            return None
