# forms.py
from django import forms
from .models import Subscriber

class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']

class NewsletterForm(forms.Form):
    subject = forms.CharField(max_length=200)
    content = forms.CharField(widget=forms.Textarea)
