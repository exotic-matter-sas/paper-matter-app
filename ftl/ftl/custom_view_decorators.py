from django.shortcuts import redirect

from core.models import FTLUser, FTLOrg


def _redirect_to_setup_step_to_complete(first_org_state, admin_state):
    """Logic to redirect user to appropriate view if required setup state isn't meet"""
    if admin_state:
        return redirect('login')
    else:
        if first_org_state:
            return redirect('setup:create_admin')
        else:
            return redirect('setup:create_first_org')


def setup_state_required(**excepted_setup_state):
    """
    Decorator for views that check that expected setup state is meet,
    if excepted setup not meet it call _redirect_to_setup_step_to_complete
    """

    def decorator(view_func):
        def _wrapped_view(*args, **kwargs):
            state_error = False
            first_org_state = FTLOrg.objects.count() > 0
            admin_state = FTLUser.objects.filter(is_staff=True).count() > 0
            complete_state = first_org_state and admin_state

            if 'complete' in excepted_setup_state:
                if complete_state != excepted_setup_state['complete']:
                    state_error = True
            else:
                if 'first_org' in excepted_setup_state:
                    if first_org_state != excepted_setup_state['first_org']:
                        state_error = True
                if 'admin' in excepted_setup_state:
                    if admin_state != excepted_setup_state['admin']:
                        state_error = True

            if state_error:
                return _redirect_to_setup_step_to_complete(first_org_state, admin_state)
            else:
                return view_func(*args, **kwargs)

        return _wrapped_view
    return decorator
