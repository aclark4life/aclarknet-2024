from itertools import chain

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..forms.project import ProjectForm
from ..models.client import Client
from ..models.contact import Contact
from ..models.invoice import Invoice
from ..models.project import Project
from ..models.task import Task
from .base import BaseView

if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class BaseProjectView(BaseView, UserPassesTestMixin):
    model = Project
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ProjectForm
    form_class = ProjectForm
    template_name = "edit.html"
    order_by = ["archived", "name", "-created"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["client", "start_date", "end_date", "team", "description"]

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        else:
            return False


class ProjectListView(BaseProjectView, ListView):
    model = Project
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_create"] = "%s_create" % self.model_name
        context["url_view"] = "%s_view" % self.model_name
        return context


class ProjectCreateView(BaseProjectView, CreateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_view")

    def get_success_url(self):
        client_id = self.request.GET.get("client_id")
        if client_id:
            return reverse_lazy("client_view", args=[client_id])
        else:
            return reverse_lazy("project_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        client = None
        client_id = self.request.GET.get("client_id")
        if client_id:
            client = Client.objects.get(id=client_id)
        context["form"].initial = {
            "start_date": now,
            "end_date": now + timezone.timedelta(days=366),
            "client": client,
        }
        if settings.USE_FAKE:
            context["form"].initial.update(
                {"name": fake.text(), "description": fake.text()}
            )
        return context

    def form_valid(self, form):
        client_id = self.request.GET.get("client_id")
        obj = form.save()
        if client_id:
            client = Client.objects.get(pk=client_id)
            client.project_set.add(obj)
            return HttpResponseRedirect(reverse("client_view", args=[client_id]))
        return super().form_valid(form)


class ProjectDetailView(BaseProjectView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        project = self.get_object()
        notes = project.notes.all()
        tasks = Task.objects.filter(project=project)
        client = project.client
        company = None
        contacts = Contact.objects.none()
        if client:
            company = client.company
            contacts = client.contact_set.all()
        invoices = Invoice.objects.filter(project=project).order_by(
            "-created", "archived"
        )
        queryset_related = [q for q in [contacts, tasks, notes, invoices] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        if company:
            queryset_related.insert(0, company)
        if client:
            queryset_related.insert(0, client)
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ProjectUpdateView(BaseProjectView, UpdateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        # Retrieve the object to be edited
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("project_view", args=[self.object.pk])


class ProjectDeleteView(BaseProjectView, DeleteView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Project.objects.all()


class ProjectCopyView(BaseProjectView, CreateView):
    model = Project
    form_model = ProjectForm
    success_url = reverse_lazy("project_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return Project.objects.all()

    def get_initial(self):
        original_project = Project.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_project.name,
        }

    def form_valid(self, form):
        new_project = form.save(commit=False)
        new_project.pk = None
        new_project.save()
        return super().form_valid(form)
