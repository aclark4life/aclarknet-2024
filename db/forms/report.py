from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms
from django.utils import timezone
from faker import Faker

from ..models.contact import Contact
from ..models.report import Report

fake = Faker()


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = (
            "name",
            "date",
            "hours",
            "amount",
            "cost",
            "net",
            "clients",
            "invoices",
            "projects",
            "tasks",
            "contacts",
            "user",
            "company",
            "team",
            "archived",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(
                Field("name", css_class="form-control bg-transparent border"),
                css_class="col-sm-4",
            ),
            Div(Field("date", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("hours", css_class="form-control"), css_class="col-sm-4"),
            Div(Field("amount", css_class="form-control"), css_class="col-sm-4"),
            css_class="row",
        )

    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "col-2"}),
        required=False,
        initial=timezone.now,
    )

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(archived=False),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )


class AdminReportForm(ReportForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Retrieve the existing layout object
        layout = self.helper.layout
        # Make modifications to the layout object
        layout.append(
            Div(Field("net", css_class="form-control"), css_class="col-sm-4"),
        )
        layout.append(
            Div(Field("cost", css_class="form-control"), css_class="col-sm-4")
        )
        layout.append(
            Div(Field("clients", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("projects", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("tasks", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("invoices", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("user", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(Field("company", css_class="form-control"), css_class="col-sm-6"),
        )
        layout.append(
            Div(
                Field("team", css_class="form-control bg-transparent border"),
                css_class="col-sm-6",
            ),
        )
        layout.append(
            Div(
                Field("contacts", css_class="form-control"),
                css_class="col-sm-6",
            ),
        )

        # Sort choices for contacts field
        choices = self.fields["contacts"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["contacts"].choices = sorted_choices

        # Sort choices for user field
        choices = self.fields["user"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["user"].choices = sorted_choices
