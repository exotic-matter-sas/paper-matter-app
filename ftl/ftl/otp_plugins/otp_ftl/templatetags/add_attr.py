#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.
import json

from django import template

register = template.Library()


@register.filter(name='add_attr')
def add_attr(field, key_val_json):
    attrs = json.loads(key_val_json)

    return field.as_widget(attrs=attrs)
