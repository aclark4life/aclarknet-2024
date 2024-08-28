from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms
from django.conf import settings
from django.utils import timezone

from ..models.contact import Contact
from ..models.invoice import Invoice


class InvoiceForm(forms.ModelForm):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol, Document Type
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("archived"), css_class="col-sm-3"),
            Div(
                Field("subject", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(Field("doc_type", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("company", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("start_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("end_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("issue_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("due_date", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("client", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("po_number", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("project", css_class="form-control"), css_class="col-sm-12"),
            Div(Field("task", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("user", css_class="form-control"), css_class="col-sm-6"),
            Div(Field("contacts", css_class="form-control"), css_class="col-sm-12"),
            css_class="row mx-1",
        )

        # Get the choices for the field
        choices = self.fields["client"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["client"].choices = sorted_choices

        # Get the choices for the field
        choices = self.fields["contacts"].choices
        sorted_choices = sorted(choices, key=lambda choice: choice[1])
        self.fields["contacts"].choices = sorted_choices

        self.fields["company"].empty_label = None

    class Meta:
        model = Invoice
        fields = (
            "client",
            "user",
            "project",
            "task",
            "po_number",
            "subject",
            "doc_type",
            "company",
            "issue_date",
            "start_date",
            "end_date",
            "due_date",
            "contacts",
            "archived",
        )
        widgets = {
            "ein": forms.widgets.NumberInput(),
            "po_number": forms.widgets.NumberInput(),
            "sa_number": forms.widgets.NumberInput(),
        }

    # times = forms.ModelMultipleChoiceField(
    #     queryset=Time.objects.filter(archived=False),
    #     widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    #     required=False,
    # )

    issue_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    due_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
        initial=timezone.now,
    )

    doc_type = forms.CharField(
        widget=forms.Select(choices=list(settings.DOC_TYPES.items())), required=False
    )

    contacts = forms.ModelMultipleChoiceField(
        queryset=Contact.objects.filter(archived=False),
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
        required=False,
    )
