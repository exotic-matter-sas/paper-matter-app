from django.utils.translation import gettext_lazy as _


def get_api_error(code):
    return {
        'code': code,
        'details': ERROR_CODES_DETAILS[code]
    }


ERROR_CODES_DETAILS = {
    'folder_name_unique_for_org_level': _('A folder with this name already exist'),
    'folder_parent_invalid': _('A folder can\'t be move inside one of its children')
}


class PluginUnsupportedStorage(Exception):
    pass
