#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from django import forms


class EmailSendForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)
