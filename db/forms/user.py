from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    rate = forms.FloatField(required=False)
    mail = forms.BooleanField(required=False)
    address = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 4, "cols": 40})
    )

    class Meta:
        model = User
        fields = [
            "is_active",
            "username",
            "first_name",
            "last_name",
            "email",
            "rate",
            "mail",
            "address",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = getattr(self.instance, "profile", None)
        if profile:
            self.fields["rate"].initial = profile.rate
            self.fields["mail"].initial = profile.mail
            self.fields["address"].initial = profile.address

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("mail", css_class=""), css_class="col-sm-12"),
            Div(
                Field("username", css_class="form-control bg-transparent border"),
                css_class="col-sm-4",
            ),
            Div(Field("email", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("rate", css_class="form-control"), css_class="col-sm-4"),
            Div(
                Field("first_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("last_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = getattr(user, "profile", None)
        if profile:
            profile.rate = self.cleaned_data["rate"]
            profile.address = self.cleaned_data["address"]
            profile.mail = self.cleaned_data["mail"]
        if commit:
            user.save()
        if profile and commit:
            profile.save()
        return user
