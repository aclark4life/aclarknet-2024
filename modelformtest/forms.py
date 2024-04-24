from django import forms
from .models import TestModel
from .models import MarketingEmailMessage


class TestModelForm(forms.ModelForm):
    class Meta:
        model = TestModel
        fields = ["name", "email", "age", "is_active", "is_subscribed"]


class MarketingEmailMessageForm(forms.ModelForm):
    class Meta:
        model = MarketingEmailMessage
        fields = ["subject", "message"]
