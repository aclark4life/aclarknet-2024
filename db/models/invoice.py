from db.models.base import BaseModel
from db.models.client import Client
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.shortcuts import reverse


class Invoice(BaseModel):
    """
    Issue Date, Last Payment Date, Invoice ID, PO Number, Client, Subject,
    Invoice Amount, Paid Amount, Balance, Subtotal, Discount, Tax, Tax2,
    Currency, Currency Symbol
    """

    subject = models.CharField(max_length=300, blank=True, null=True)
    issue_date = models.DateField(
        "Issue Date", blank=True, default=timezone.now, null=True
    )
    due_date = models.DateField("Due", blank=True, null=True)
    last_payment_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(
        "Start Date", blank=True, default=timezone.now, null=True
    )
    end_date = models.DateField("End Date", blank=True, default=timezone.now, null=True)
    po_number = models.CharField("PO Number", max_length=300, blank=True, null=True)
    sa_number = models.CharField(
        "Subcontractor Agreement Number", max_length=300, blank=True, null=True
    )
    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey("Task", blank=True, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(
        "Invoice Amount", blank=True, null=True, max_digits=12, decimal_places=2
    )
    paid_amount = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    balance = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    subtotal = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    discount = models.IntegerField(blank=True, null=True)
    ein = models.IntegerField("EIN", blank=True, null=True)
    tax = models.IntegerField(blank=True, null=True)
    tax2 = models.IntegerField(blank=True, null=True)
    project = models.ForeignKey(
        "Project", blank=True, null=True, on_delete=models.SET_NULL
    )
    currency = models.CharField(
        default="United States Dollar - USD", max_length=300, blank=True, null=True
    )
    currency_symbol = models.CharField(
        default="$", max_length=300, blank=True, null=True
    )

    # https://stackoverflow.com/a/6062320/185820
    class Meta:
        ordering = ["subject"]

    doc_type = models.CharField(max_length=300, blank=True, null=True)
    gross = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    contacts = models.ManyToManyField("Contact", blank=True)

    reset = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse("invoice_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.subject:
            self.subject = self.__str__()
        super().save(*args, **kwargs)
