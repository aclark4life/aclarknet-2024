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
from faker import Faker

from ..forms.contact import ContactForm
from ..models import Contact
from .base import BaseView

fake = Faker()


class BaseContactView(BaseView, UserPassesTestMixin):
    model = Contact
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ContactForm
    form_class = ContactForm
    template_name = "edit.html"
    order_by = ["archived", "name"]
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["first_name", "last_name", "url", "number"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class ContactListView(BaseContactView, ListView):
    template_name = "index.html"


class ContactCreateView(BaseContactView, CreateView):
    def get_success_url(self):
        return reverse_lazy("contact_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_name = self.model_name

        if settings.USE_FAKE:
            first_name = fake.first_name()
            last_name = fake.last_name()
            context["form"].initial = {
                "name": " ".join([first_name, last_name]),
                "first_name": first_name,
                "last_name": last_name,
                "email": fake.email(),
            }
        context["model_name"] = model_name
        model_name_plural = self.model._meta.verbose_name_plural
        context["model_name_plural"] = model_name_plural
        context["url_index"] = "%s_index" % model_name
        context["%s_nav" % model_name] = True
        return context


class ContactDetailView(BaseContactView, DetailView):
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        contact = self.get_object()
        notes = contact.notes.all()
        client = contact.client
        queryset_related = [q for q in [notes] if q.exists()]
        if client:
            queryset_related.insert(0, client)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)
        return context


class ContactUpdateView(BaseContactView, UpdateView):
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
        return reverse_lazy("contact_view", args=[self.object.pk])


class ContactDeleteView(BaseContactView, DeleteView):
    success_url = reverse_lazy("contact_index")
    template_name = "delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["url_cancel"] = reverse_lazy(
        #     "contact_view", kwargs={"pk": self.kwargs["pk"]}
        # )
        return context

    def get_queryset(self):
        return Contact.objects.all()


class ContactCopyView(BaseContactView, CreateView):
    success_url = reverse_lazy("contact_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the model name dynamically
        model_name = self.model._meta.model_name
        context["model_name"] = model_name
        context["%s_nav" % model_name] = True
        return context

    def get_queryset(self):
        return Contact.objects.all()

    def form_valid(self, form):
        # Get the original contact object
        original_contact = Contact.objects.get(pk=self.kwargs["pk"])

        # Copy the original contact's data to a new contact object
        new_contact = original_contact

        # Save the new contact object
        new_contact.save()

        # Redirect to the success URL
        return super().form_valid(form)
