import random
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from faker import Faker

from ..forms.user import UserForm
from ..models.contact import Contact
from ..models.invoice import Invoice
from ..models.project import Project
from ..models.time import Time

from .base import BaseView

fake = Faker()


class BaseUserView(BaseView):
    model = User
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_class = UserForm
    form_model = UserForm
    order_by = ["-is_active", "username"]
    exclude = ["rate", "mail", "address"]
    url_create = f"{model_name.lower()}_create"
    url_copy = f"{model_name.lower()}_copy"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"


class BaseUserMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        # Customize the behavior when the user fails the test
        # For example, redirect them to a login page or show an error message
        # Here, we'll raise a 403 Forbidden error
        raise PermissionDenied


class UserListView(BaseUserMixin, BaseUserView, ListView):
    template_name = "index.html"


class UserDetailView(BaseUserMixin, BaseUserView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        per_page = self.request.GET.get("items_per_page", settings.PER_PAGE)

        user = self.get_object()

        notes = []
        if hasattr(user, "profile"):
            notes = user.profile.notes.all()
        projects = Project.objects.filter(team__in=[user])
        times = Time.objects.filter(user=user)
        invoices = Invoice.objects.filter(times__in=times)

        queryset_related = list(chain(notes, projects, times, invoices))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)

        times = Time.objects.filter(user=user, archived=False)
        entered = times.aggregate(total=Sum(F("hours")))
        approved = times.filter(invoice__isnull=False).aggregate(total=Sum(F("hours")))

        context["statcard"]["times"]["entered"] = entered
        context["statcard"]["times"]["approved"] = approved

        approved = approved["total"] or 0

        gross = 0
        for project in projects:
            task = project.task
            if task:
                gross = approved * project.task.rate

            cost = 0
            if hasattr(user, "profile"):
                rate = user.profile.rate
                if rate:
                    cost = approved * user.profile.rate

            net = 0
            if gross and cost:
                net = gross - cost

            gross = gross or 0
            cost = cost or 0
            net = net or 0

            context["statcards"][project.name] = {}
            context["statcards"][project.name]["name"] = project.name
            context["statcards"][project.name]["invoices"] = {}
            context["statcards"][project.name]["invoices"]["gross"] = f"{gross:.2f}"
            context["statcards"][project.name]["invoices"]["cost"] = f"{cost:.2f}"
            context["statcards"][project.name]["invoices"]["net"] = f"{net:.2f}"

        context["user"] = self.request.user
        context["user_view"] = True

        return context


class UserCreateView(BaseUserView, CreateView):
    success_url = reverse_lazy("user_index")
    template_name = "edit.html"

    def get_initial(self):
        fake_profile = fake.profile()
        # Fake GitHub token
        # token_length = 40
        # allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        # token = "".join(random.choices(allowed_chars, k=token_length))
        return {
            "username": fake_profile["username"],
            "email": fake_profile["mail"],
            "password": fake.password(),
            "rate": f"{random.random() * 100:.2f}",
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        }

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True  # Set is_active to True
        user.save()
        return super().form_valid(form)


class UserUpdateView(BaseUserMixin, BaseUserView, UpdateView):
    success_url = reverse_lazy("user_view")
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def form_valid(self, form):
        is_active = form.initial["is_active"]
        if is_active:
            form.instance.is_active = is_active
        return super().form_valid(form)

    def get_success_url(self):
        user = self.get_object()
        user_id = user.id
        return reverse("user_view", args=[user_id])


class UserDeleteView(BaseUserMixin, BaseUserView, DeleteView):
    success_url = reverse_lazy("user_index")
    template_name = "delete.html"

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        user.delete()
        messages.success(request, f"You deleted {username}!")
        return HttpResponseRedirect(reverse("user_index"))


class UserCopyView(BaseUserMixin, BaseUserView, CreateView):
    success_url = reverse_lazy("user_index")
    template_name = "edit.html"


class UserToContactView(BaseUserView, View):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            contact = Contact(
                first_name=user.first_name, last_name=user.last_name, email=user.email
            )
            contact.save()
            return HttpResponseRedirect(reverse("contact_view", args=[contact.id]))
        except User.DoesNotExist:
            return render("error.html")
