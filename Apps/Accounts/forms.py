from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

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

class EmailChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']
        labels = {
            'email': 'Nouvelle adresse e-mail'
        }
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'votre@email.com', 'required': True})
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']
        labels = {
            'username': "Nom d'utilisateur"
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'profileUsernameInput', 'required': True})
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birth_date', 'avatar']
        labels = {
            'birth_date': 'Date de naissance',
            'avatar': 'Photo de profil'
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control input-date', 
                'id': 'profileBirthdayInput', 
                'placeholder': 'jj/mm/aaaa', 
                'type': 'text' # Using text for flatpickr/cleave.js if present, or just text with placeholder
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'id': 'profileAvatarInput',
                'accept': 'image/png, image/jpeg, image/gif'
            })
        }
