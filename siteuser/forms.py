from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User


class SiteUserForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("rate",)

    rate = forms.FloatField()

    def save(self):
        instance = super().save()

        self.instance.profile.rate = self.cleaned_data["rate"]
        self.instance.profile.save()

        return instance
