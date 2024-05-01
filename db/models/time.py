from django.db import models
from db.models.base import BaseModel
from db.models.client import Client
from db.models.project import Project
from db.models.task import Task
from db.models.invoice import Invoice
from django.conf import settings
from django.utils import timezone
from django.shortcuts import reverse


class Time(BaseModel):
    """
    Date, Client, Project, Project Code, Task, Hours, Billable?,
    Invoiced?, First Name, Last Name, Department, Employee?, Billable
    Rate, Billable Amount, Cost Rate, Cost Amount, Currency,
    External Reference URL
    """

    invoiced = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    project = models.ForeignKey(
        Project,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    task = models.ForeignKey(
        Task,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    invoice = models.ForeignKey(
        Invoice,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="times",
    )
    date = models.DateField(default=timezone.now, blank=True, null=True)
    hours = models.DecimalField(
        "Hours", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    description = models.TextField(blank=True, null=True)

    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)

    # IGCE
    quantity = models.DecimalField(
        "Quantity", default=1.0, blank=True, null=True, max_digits=12, decimal_places=2
    )
    unit = models.CharField(max_length=2, blank=True, null=True)
    unit_price = models.DecimalField(
        "Unit Price",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    total_price = models.DecimalField(
        "Total Price",
        default=1.0,
        blank=True,
        null=True,
        max_digits=12,
        decimal_places=2,
    )
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)

    def get_absolute_url(self):
        return reverse("time_view", args=[str(self.id)])
