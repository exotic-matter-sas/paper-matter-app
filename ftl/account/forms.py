from django import forms


class EmailSendForm(forms.Form):
    email = forms.CharField(widget=forms.EmailInput)
