from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "archived",
            "first_name",
            "last_name",
            "name",
            "email",
            "client",
            "url",
            "number",
        )
        labels = {
            "name": "Full name",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("first_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("last_name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("email", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("number", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(
                Field("url", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("client", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )
