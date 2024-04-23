from django import forms
from .models import TestModel

class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ['name', 'email', 'age', 'is_active']  # Add or remove fields as needed
