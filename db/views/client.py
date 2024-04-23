from itertools import chain

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from rest_framework import viewsets

from ..forms.client import ClientForm
from ..models.client import Client
from ..models.company import Company
from ..models.invoice import Invoice
from ..models.task import Task
from ..serializers import ClientSerializer
from .base import BaseView

if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class ClientAPIViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.filter(publish=True).order_by("name")
    serializer_class = ClientSerializer


class BaseClientView(BaseView, UserPassesTestMixin):
    model = Client
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ClientForm
    form_class = ClientForm
    order_by = ["archived", "name"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = [
        "publish",
        "link",
        "company",
        "tags",
        "address",
        "url",
        "description",
    ]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class ClientListView(BaseClientView, ListView):
    model = Client
    template_name = "index.html"


class ClientCreateView(BaseClientView, CreateView):
    template_name = "edit.html"

    def get_success_url(self):
        return reverse_lazy("client_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companies = Company.objects.all()
        if companies:
            company = companies.first()
            context["form"].initial = {
                "company": company,
            }
        if settings.USE_FAKE:
            context["form"].initial.update(
                {
                    "name": fake.company(),
                    "url": fake.url(),
                    "description": fake.catch_phrase(),
                    "address": fake.address(),
                    "tags": fake.text(),
                }
            )
        return context

    def form_valid(self, form):
        company_id = self.request.GET.get("company_id")
        obj = form.save()
        if company_id:
            company = Company.objects.get(pk=company_id)
            company.client_set.add(obj)
            return HttpResponseRedirect(reverse("company_view", args=[company_id]))
        return super().form_valid(form)


class ClientDetailView(BaseClientView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        client = self.get_object()
        notes = client.notes.all()
        projects = client.project_set.all().order_by("archived")
        company = client.company
        contacts = client.contact_set.all()
        invoices = Invoice.objects.filter(project__in=projects)
        reports = client.report_set.all().order_by("-created")
        invoices = invoices.order_by("archived", "-created")
        tasks = Task.objects.filter(project__in=projects)
        queryset_related = [
            q
            for q in [notes, projects, contacts, invoices, tasks, reports]
            if q.exists()
        ]
        if company:
            queryset_related.insert(0, [company])
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ClientUpdateView(BaseClientView, UpdateView):
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("client_view", args=[self.object.pk])


class ClientDeleteView(BaseClientView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("client_index")

    def get_queryset(self):
        return Client.objects.all()


class ClientCopyView(BaseClientView, CreateView):
    template_name = "edit.html"

    def get_queryset(self):
        return Client.objects.all()

    def get_initial(self):
        # Get the original client object
        original_client = Client.objects.get(pk=self.kwargs["pk"])
        # Return a dictionary of initial values for the form fields
        return {
            "name": original_client.name,
            # Add more fields as needed
        }

    def form_valid(self, form):
        # Copy the original client's data to a new client object
        new_client = form.save(commit=False)
        new_client.pk = None
        new_client.save()
        # Redirect to the success URL
        return super().form_valid(form)
