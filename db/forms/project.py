from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models.client import Client
from ..models.project import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            "name",
            "description",
            "client",
            "task",
            "start_date",
            "end_date",
            "team",
            "archived",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.fields["client"].empty_label = "Select a client"
        self.fields[
            "client"
        ].queryset = Client.objects.all()  # Fetch all clients for the dropdown
        self.helper.layout = Div(
            Div(Field("archived"), css_class="col-sm-12"),
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
            Div(Field("task", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("start_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("end_date", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("team", css_class="form-control"), css_class="col-sm-12"),
            Div(Field("client", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )

        # Get the choices for the field
        choices = self.fields["team"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["team"].choices = sorted_choices
