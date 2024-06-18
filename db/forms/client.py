from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            "archived",
            "publish",
            "link",
            "name",
            "description",
            "address",
            "url",
            "company",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("archived"), css_class="col-sm-3"),
            Div(Field("publish"), css_class="col-sm-3"),
            Div(Field("link"), css_class="col-sm-3"),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("url", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("address", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("company", css_class="form-control"), css_class="col-sm-12"),
            Div(Field("tags", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )
