from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models.task import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("name", "rate", "unit", "archived")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("archived", css_class=""), css_class="col-sm-3"),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("rate", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("unit", css_class="form-control"), css_class="col-sm-6"),
            css_class="row",
        )
