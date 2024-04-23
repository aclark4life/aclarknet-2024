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

from ..forms.task import TaskForm
from ..models.project import Project
from ..models.task import Task
from .base import BaseView

if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class BaseTaskView(BaseView, UserPassesTestMixin):
    model = Task
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = TaskForm
    form_class = TaskForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["rate", "unit"]
    order_by = ["archived", "name", "-created"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class TaskListView(BaseTaskView, ListView):
    template_name = "index.html"


class TaskCreateView(BaseTaskView, CreateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_view")

    def get_success_url(self):
        return reverse_lazy("task_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.USE_FAKE:
            context["form"].initial = {
                "name": fake.text(),
                "rate": fake.pydecimal(left_digits=3, right_digits=2, positive=True),
            }
        return context

    def form_valid(self, form):
        project_id = self.request.GET.get("project_id")
        obj = form.save()
        if project_id:
            project = Project.objects.get(pk=project_id)
            obj.project_set.add(project)
            return HttpResponseRedirect(reverse("project_view", args=[project_id]))
        return super().form_valid(form)


class TaskDetailView(BaseTaskView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        task = self.get_object()
        notes = task.notes.all()
        projects = Project.objects.filter(task=task)
        queryset_related = [q for q in [notes, projects] if q.exists()]
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class TaskUpdateView(BaseTaskView, UpdateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_view")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("task_view", args=[self.object.pk])


class TaskDeleteView(BaseTaskView, DeleteView):
    form_model = TaskForm
    success_url = reverse_lazy("task_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Task.objects.all()


class TaskCopyView(BaseTaskView, CreateView):
    form_model = TaskForm
    success_url = reverse_lazy("task_index")

    def get_queryset(self):
        return Task.objects.all()

    def get_initial(self):
        original_task = Task.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_task.name,
        }

    def form_valid(self, form):
        new_task = form.save(commit=False)
        new_task.pk = None
        new_task.save()
        return super().form_valid(form)
