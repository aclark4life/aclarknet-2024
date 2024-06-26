from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models import Client, Company


class CompanyForm(forms.ModelForm):
    client_set = forms.ModelMultipleChoiceField(
        queryset=Client.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
        label="Clients",
    )

    class Meta:
        model = Company
        fields = ("name", "url", "description", "client_set", "archived")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("archived"), css_class="col-sm-3"),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("url", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("client_set", css_class="vh-100"), css_class="col-sm-12"),
            css_class="row",
        )

        # Set the initial value of the client_set field
        if self.instance.pk:
            self.fields["client_set"].initial = self.instance.client_set.all()
