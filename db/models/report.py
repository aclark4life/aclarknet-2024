from django.db import models
from django.contrib.postgres.fields import HStoreField


from db.models.base import BaseModel
from django.utils import timezone
from django.conf import settings
from django.shortcuts import reverse


class Report(BaseModel):
    date = models.DateField(default=timezone.now)
    hours = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    net = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    clients = models.ManyToManyField("Client", blank=True)
    projects = models.ManyToManyField("Project", blank=True)
    tasks = models.ManyToManyField("Task", blank=True)
    invoices = models.ManyToManyField("Invoice", blank=True)
    contacts = models.ManyToManyField("Contact", blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL
    )
    reports = models.ManyToManyField("Report", blank=True)
    company = models.ForeignKey(
        "Company", blank=True, null=True, on_delete=models.SET_NULL
    )
    team = HStoreField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("report_view", args=[str(self.id)])
