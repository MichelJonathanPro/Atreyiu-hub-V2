from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requis pour l\'activation du compte.')
    # Honeypot field
    website_url = forms.CharField(required=False, widget=forms.HiddenInput(), label="Laisser vide")

    class Meta:
        model = User
        fields = ("username", "email")

    def clean_website_url(self):
        url = self.cleaned_data.get('website_url')
        if url:
            raise forms.ValidationError("Bot detected!")
        return url
