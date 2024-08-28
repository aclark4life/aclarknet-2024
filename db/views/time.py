from itertools import chain

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from faker import Faker

from ..forms.time import AdminTimeForm, TimeForm
from ..models.client import Client
from ..models.invoice import Invoice
from ..models.project import Project
from ..models.task import Task
from ..models.time import Time

from .base import BaseView

fake = Faker()


class BaseTimeView(BaseView, UserPassesTestMixin):
    model = Time
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = TimeForm
    form_class = TimeForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client", "project", "task", "invoice"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminTimeForm

        form = super().get_form(form_class)

        projects = Project.objects.filter(team__in=[self.request.user], archived=False)
        invoices = Invoice.objects.filter(
            project__in=projects, archived=False, doc_type="invoice"
        )

        if invoices:
            form.fields["invoice"].empty_label = None

        # form.fields["invoice"].queryset = invoices

        if self.request.user.is_superuser:
            project = projects.first()
            if project:
                form.fields["task"].empty_label = None
                if project.task:
                    form.fields["task"].queryset = Task.objects.filter(
                        project__in=projects,
                    )
                form.fields["project"].empty_label = None
                form.fields["project"].queryset = projects
                form.fields["client"].empty_label = None
                form.fields["client"].queryset = Client.objects.filter(
                    project__in=projects,
                )

        form.fields["user"].empty_label = None
        form.fields["user"].queryset = User.objects.filter(pk=self.request.user.id)

        return form


class TimeCreateView(BaseTimeView, CreateView):
    success_url = reverse_lazy("time_view")

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_id = None
        description = None
        project_id = None
        task_id = None

        if settings.USE_FAKE:
            description = fake.text()

        context["form"].initial = {
            "description": description,
            "user": self.request.user.id,
        }

        invoice_id = self.request.GET.get("invoice_id")

        try:
            invoice = Invoice.objects.get(pk=invoice_id)
        except (ValueError, Invoice.DoesNotExist):
            invoice = None

        if invoice:
            if invoice.client:
                client_id = invoice.client.id
            if invoice.project:
                project_id = invoice.project.id

                if invoice.project.task:
                    task_id = invoice.project.task.id

        context["form"].initial.update(
            {
                "client": client_id,
                "invoice": invoice_id,
                "project": project_id,
                "task": task_id, 
            }
        )
        return context


class TimeListView(BaseTimeView, ListView):
    template_name = "index.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False


class TimeDetailView(BaseTimeView, DetailView):
    template_name = "view.html"

    def test_func(self):
        time_entry = self.get_object()
        time_user = time_entry.user
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated and self.request.user == time_user:
            return True
        else:
            return False

    def get_context_data(self, **kwargs):
        time = self.get_object()
        if time.invoice:
            queryset_related = list(chain([time.invoice]))
            self.queryset_related = queryset_related
            self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class TimeUpdateView(BaseTimeView, UpdateView):
    success_url = reverse_lazy("time_view")

    def form_valid(self, form):
        user_id = form.initial["user"]
        if user_id:
            user = User.objects.get(pk=user_id)
            form.instance.user = user
        return super().form_valid(form)

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])


class TimeDeleteView(BaseTimeView, DeleteView):
    success_url = reverse_lazy("time_index")
    template_name = "delete.html"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse_lazy("time_index")
        else:
            return reverse_lazy("dashboard")

    def get_queryset(self):
        return Time.objects.all()


class TimeCopyView(BaseTimeView, CreateView):
    success_url = reverse_lazy("time_index")

    def get_success_url(self):
        return reverse_lazy("time_view", args=[self.object.pk])

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif self.request.user.is_authenticated:
            return True
        else:
            return False

    def get_queryset(self):
        return Time.objects.all()

    def get_initial(self):
        original_time = Time.objects.get(pk=self.kwargs["pk"])
        # tomorrow = original_time.date + timezone.timedelta(days=1)
        return {
            "user": original_time.user,
            "name": original_time.name,
            "hours": original_time.hours,
            "description": original_time.description,
            # "date": tomorrow,
            "date": timezone.now,
            "invoice": original_time.invoice,
            "task": original_time.task,
            "project": original_time.project,
            "client": original_time.client,
        }

    def form_valid(self, form):
        new_time = form.save(commit=False)
        new_time.pk = None
        new_time.save()
        return super().form_valid(form)
