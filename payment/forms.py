# forms.py
from django import forms
from .models import Wallet

class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['currency', 'address']

    def clean_currency(self):
        currency = self.cleaned_data.get('currency')
        # Add custom validation for currency here if needed
        return currency

    def clean_address(self):
        address = self.cleaned_data.get('address')
        # Add custom validation for address here if needed
        return address
