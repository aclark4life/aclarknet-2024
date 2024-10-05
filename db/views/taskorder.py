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

from ..forms.taskorder import TaskOrderForm
from ..models.project import Project
from ..models.taskorder import TaskOrder
from .base import BaseView

if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class BaseTaskOrderView(BaseView, UserPassesTestMixin):
    model = TaskOrder
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = TaskOrderForm
    form_class = TaskOrderForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    order_by = ["archived", "name", "-created"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class TaskOrderListView(BaseTaskOrderView, ListView):
    template_name = "index.html"


class TaskOrderCreateView(BaseTaskOrderView, CreateView):
    form_model = TaskOrderForm
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


class TaskOrderDetailView(BaseTaskOrderView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TaskOrderUpdateView(BaseTaskOrderView, UpdateView):
    form_model = TaskOrderForm
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


class TaskOrderDeleteView(BaseTaskOrderView, DeleteView):
    form_model = TaskOrderForm
    success_url = reverse_lazy("task_index")
    template_name = "delete.html"

    def get_queryset(self):
        return TaskOrder.objects.all()


class TaskOrderCopyView(BaseTaskOrderView, CreateView):
    form_model = TaskOrderForm
    success_url = reverse_lazy("task_index")

    def get_queryset(self):
        return TaskOrder.objects.all()

    def get_initial(self):
        original_task = TaskOrder.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_task.name,
        }

    def form_valid(self, form):
        new_task = form.save(commit=False)
        new_task.pk = None
        new_task.save()
        return super().form_valid(form)
