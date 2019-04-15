from django.shortcuts import redirect

from core.models import FTLUser, FTLOrg


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


def setup_state_required(excepted_setup_state):
    """
    Decorator for views that check that expected setup state is meet:
    - if excepted setup meet it returns decorated view
    - else it call _redirect_to_setup_step_to_complete
    """

    def decorator(view_func):
        def _wrapped_view(*args, **kwargs):
            state_error = True
            first_org_state = FTLOrg.objects.count() > 0
            admin_state = FTLUser.objects.filter(is_staff=True).count() > 0

            none_state = not (first_org_state or admin_state)

            if excepted_setup_state == SetupState.none:
                if none_state:
                    state_error = False
            elif excepted_setup_state == SetupState.first_org_created:
                if first_org_state and not admin_state:
                    state_error = False
            elif excepted_setup_state == SetupState.admin_created:
                if first_org_state and admin_state:
                    state_error = False
            else:
                raise ValueError(f'excepted_setup_state is not valid, accepted value are:'
                                 f'{[attr for attr in dir(SetupState) if not attr.startswith("_")]}')

            if state_error:
                return _redirect_to_setup_step_to_complete(first_org_state, admin_state)
            else:
                return view_func(*args, **kwargs)

        return _wrapped_view
    return decorator
