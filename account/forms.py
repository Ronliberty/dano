from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile




class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone_number']
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Enter your bio...',
                'style': '''width: 95%; height: 30%; overflow-x: hidden; margin: 1.5rem 1.5rem; padding: 10px; border-radius: 8px;
                margin-top: 20px; margin-bottom: 20px; border: 1px solid #ccc; font-size: 14px; box-sizing: border-box;''',
                'class': 'responsive-input'  # Adding a class for mobile responsiveness
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'style': '''width: 90%; overflow-x: hidden; padding: 10px; margin: 1.5rem 1.5rem; margin-top: 20px; margin-bottom: 20px;
                border: 1px solid #ccc; border-radius: 8px; cursor: pointer; box-sizing: border-box;''',
                'class': 'responsive-input'  # Adding a class for mobile responsiveness
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number',
                'style': '''width: 90%; margin: 1.5rem 1.5rem; overflow-x: hidden; margin-top: 20px; margin-bottom: 20px; padding: 10px;
                border-radius: 8px; border: 1px solid #ccc; font-size: 14px; box-sizing: border-box;''',
                'class': 'responsive-input'  # Adding a class for mobile responsiveness
            }),
        }

