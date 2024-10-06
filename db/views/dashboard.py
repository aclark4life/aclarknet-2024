from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.views.generic import ListView

from ..models.note import Note
from ..models.client import Client
from ..models.company import Company
from ..models.contact import Contact
from ..models.invoice import Invoice
from ..models.project import Project
from ..models.report import Report
from ..models.task import Task
from ..models.time import Time
from .base import BaseView


def get_queryset(model_class, filter_by=None, order_by=None):
    _ = {}

    queryset = model_class.objects.all()

    if filter_by:
        queryset = queryset.filter(**filter_by)

    if order_by:
        queryset = queryset.order_by(*order_by)

    _["queryset"] = queryset

    return _


class DashboardView(BaseView, UserPassesTestMixin, ListView):
    template_name = "dashboard/index.html"
    dashboard = True

    def get_queryset(self):
        return []

    def test_func(self):
        return self.request.user.is_authenticated

    def handle_no_permission(self):
        # Customize the behavior when the user fails the test
        # For example, redirect them to a login page or show an error message
        # Here, we'll raise a 403 Forbidden error
        return HttpResponseRedirect(reverse("account_login"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["overview_nav"] = True

        filter_by = {"archived": False}

        invoices = get_queryset(
            Invoice,
            filter_by={"archived": False},
            order_by=["-created"],
        )

        context["invoices"] = invoices
        context["companies"] = get_queryset(
            Company, filter_by=filter_by, order_by=["name"]
        )
        context["projects"] = get_queryset(
            Project, filter_by=filter_by, order_by=["name"]
        )
        context["notes"] = get_queryset(
            Note, filter_by=filter_by, order_by=["-created"]
        )
        context["tasks"] = get_queryset(Task, filter_by=filter_by, order_by=["name"])
        context["contacts"] = get_queryset(
            Contact, filter_by=filter_by, order_by=["last_name"]
        )
        context["clients"] = get_queryset(
            Client, filter_by=filter_by, order_by=["name"]
        )
        context["reports"] = get_queryset(
            Report, filter_by=filter_by, order_by=["-created"]
        )

        if not self.request.user.is_superuser:
            filter_by = {"archived": False, "user": self.request.user}

        times = get_queryset(Time, filter_by=filter_by, order_by=["-archived", "-date"])

        context["times"] = times

        entered = times["queryset"].aggregate(total=Sum(F("hours")))
        approved = (
            times["queryset"]
            .filter(invoice__isnull=False)
            .aggregate(total=Sum(F("hours")))
        )

        context["statcard"]["times"]["entered"] = entered
        context["statcard"]["times"]["approved"] = approved

        entered = entered["total"] or 0
        approved = approved["total"] or 0

        gross = invoices["queryset"].aggregate(amount=Sum(F("amount")))["amount"]
        cost = invoices["queryset"].aggregate(cost=Sum(F("cost")))["cost"]
        net = invoices["queryset"].aggregate(net=Sum(F("net")))["net"]

        gross = gross or 0
        cost = cost or 0
        net = net or 0

        context["statcards"] = {}
        context["statcards"]["dashboard"] = {}
        context["statcards"]["dashboard"]["invoices"] = {}
        context["statcards"]["dashboard"]["invoices"]["gross"] = gross
        context["statcards"]["dashboard"]["invoices"]["cost"] = cost
        context["statcards"]["dashboard"]["invoices"]["net"] = net

        context["dataset_times"] = [int(entered), int(approved)]
        context["dataset_invoices"] = [int(gross), int(cost), int(net)]
        context["dashboard"] = self.dashboard

        return context
