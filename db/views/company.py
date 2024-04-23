import random
from itertools import chain

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..forms.company import CompanyForm
from ..models.client import Client
from ..models.company import Company
from ..models.contact import Contact
from ..models.project import Project
from ..models.task import  Task
from .base import BaseView

if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class BaseCompanyView(BaseView, UserPassesTestMixin):
    model = Company
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = CompanyForm
    form_class = CompanyForm
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client_set", "description", "url"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class CompanyListView(BaseCompanyView, ListView):
    template_name = "index.html"


class CompanyCreateView(BaseCompanyView, CreateView):
    model = Company
    form_model = CompanyForm
    success_url = reverse_lazy("company_view")
    template_name = "edit.html"

    def get_success_url(self):
        return reverse_lazy("company_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Set the initial value of the client_set field
        clients = list(Client.objects.all())
        random_clients = random.sample(clients, k=len(clients))  # Select random clients
        initial_values = [client.pk for client in random_clients]
        context["form"].initial = {
            "client_set": initial_values,
        }
        if settings.USE_FAKE:
            context["form"].initial["name"] = fake.company()
            context["form"].initial["description"] = fake.catch_phrase()
            context["form"].initial["url"] = fake.url()
        return context

    def form_valid(self, form):
        # Set the company's creator to the current user
        form.instance.creator = self.request.user
        # Save the company instance without committing to the database
        company = form.save(commit=False)
        # Add the selected clients to the company
        company.save()
        company.client_set.set(form.cleaned_data["client_set"])
        # Commit the changes to the database
        form.save_m2m()
        return super().form_valid(form)


class CompanyDetailView(BaseCompanyView, DetailView):
    model = Company
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        company = self.get_object()
        clients = company.client_set.all().order_by("archived", "name")
        projects = Project.objects.filter(client__in=clients).order_by(
            "archived", "name"
        )
        notes = company.notes.all()
        tasks = Task.objects.filter(project__in=projects).order_by("archived", "name")
        contacts = Contact.objects.filter(client__in=clients).order_by(
            "archived", "name"
        )
        queryset_related = [
            q for q in [clients, contacts, notes, projects, tasks] if q.exists()
        ]
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class CompanyUpdateView(BaseCompanyView, UpdateView):
    model = Company
    form_model = CompanyForm
    template_name = "edit.html"

    def form_valid(self, form):
        # Save the form data
        response = super().form_valid(form)
        # Add the selected clients to the company
        form.instance.client_set.set(form.cleaned_data["client_set"])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        # Retrieve the object to be edited
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("company_view", args=[self.object.pk])


class CompanyDeleteView(BaseCompanyView, DeleteView):
    model = Company
    form_model = CompanyForm
    success_url = reverse_lazy("company_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Company.objects.all()


class CompanyCopyView(BaseCompanyView, CreateView):
    model = Company
    form_model = CompanyForm
    template_name = "edit.html"

    def get_queryset(self):
        return Company.objects.all()

    def get_initial(self):
        # Get the original company object
        original_company = Company.objects.get(pk=self.kwargs["pk"])

        # Return a dictionary of initial values for the form fields
        return {
            "name": original_company.name,
            # Add more fields as needed
        }

    def form_valid(self, form):
        # Copy the original company's data to a new company object
        new_company = form.save(commit=False)
        new_company.pk = None
        new_company.save()

        # Redirect to the success URL
        return super().form_valid(form)
