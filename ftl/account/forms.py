from django import forms


class EmailSendForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput)
