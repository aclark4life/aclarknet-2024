from crispy_forms.helper import FormHelper
from crispy_forms.layout import HTML, Div, Field
from django import forms
from django.utils import timezone

from ..models.time import Time


class TimeForm(forms.ModelForm):
    """ """

    class Meta:
        model = Time
        fields = [
            "user",
            "date",
            "hours",
            "description",
            "client",
            "project",
            "task",
            "invoice",
            "archived",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("archived"), css_class="col-sm-12"),
            Div(Field("date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("hours", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("user", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("invoice", css_class="form-control"), css_class="col-sm-6"),
            Div(
                Field("description", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            css_class="row",
        )

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )


class AdminTimeForm(TimeForm):
    """ """

    hours = forms.FloatField(
        required=False,
        initial=1.0,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retrieve the existing layout object
        layout = self.helper.layout

        # Make modifications to the layout object
        layout.append(
            Div(Field("task", css_class="form-control"), css_class="col-sm-4")
        )
        layout.append(
            Div(Field("project", css_class="form-control"), css_class="col-sm-4")
        )
        layout.append(
            Div(Field("client", css_class="form-control"), css_class="col-sm-4")
        )

        # Sort choices for user field
        choices = self.fields["user"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["user"].choices = sorted_choices
