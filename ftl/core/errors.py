from django.utils.translation import gettext_lazy as _


def get_api_error(code):
    return {
        'code': code,
        'details': ERROR_CODES_DETAILS[code]
    }


ERROR_CODES_DETAILS = {
    'folder_name_unique_for_org_level': _('a folder with this name already exist')
}


class PluginUnsupportedStorage(Exception):
    pass
