from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from ..forms.note import NoteForm
from ..models.note import Note
from .base import BaseView


if settings.USE_FAKE:
    from faker import Faker

    fake = Faker()


class BaseNoteView(BaseView, UserPassesTestMixin):
    model = Note
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = NoteForm
    form_class = NoteForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = ["html"]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class NoteListView(BaseNoteView, ListView):
    model = Note
    template_name = "index.html"


class NoteListFullScreen(NoteListView, ListView):
    model = Note
    template_name = "notes/fullscreen.html"


class NoteCreateView(BaseNoteView, CreateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")

    def get_success_url(self):
        return reverse_lazy("note_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.USE_FAKE:
            context["form"].initial = {
                "title": fake.text(),
                "text": fake.text(),
            }
        return context


class NoteDetailView(BaseNoteView, DetailView):
    model = Note
    template_name = "view.html"
    url_export_pdf = "note_export_pdf"
    url_email_pdf = "note_email_pdf"
    url_email_text = "note_email_text"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        return context


class NoteUpdateView(BaseNoteView, UpdateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_view")

    def form_valid(self, form):
        html = form.initial["html"]
        if html:
            form.instance.html = html
        return super().form_valid(form)

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
        return reverse_lazy("note_view", args=[self.object.pk])


class NoteDeleteView(BaseNoteView, DeleteView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Note.objects.all()


class NoteCopyView(BaseNoteView, CreateView):
    model = Note
    form_model = NoteForm
    success_url = reverse_lazy("note_index")

    def get_queryset(self):
        return Note.objects.all()

    def form_valid(self, form):
        # Get the original note object
        original_note = Note.objects.get(pk=self.kwargs["pk"])

        # Copy the original note's data to a new note object
        new_note = original_note

        # Save the new note object
        new_note.save()

        # Redirect to the success URL
        return super().form_valid(form)


class NoteEmailTextView(BaseNoteView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)

        email = EmailMessage(
            subject=obj.title,
            body=obj.text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.DEFAULT_FROM_EMAIL],
        )

        contacts = obj.contacts.all()

        successes = []
        failures = []

        if contacts:
            for contact in contacts:
                email.to = [contact.email]
                try:
                    email.send()
                except:  # noqa
                    failures.append(contact.email)
                else:
                    successes.append(contact.email)
        else:
            try:
                email.send()
            except:  # noqa
                failures.append(settings.DEFAULT_FROM_EMAIL)
            else:
                successes.append(settings.DEFAULT_FROM_EMAIL)
        if successes:
            messages.success(
                request, f"Email sent successfully to: {', '.join(successes)}."
            )
        if failures:
            messages.warning(
                request, f"Failed to send email to: {', '.join(failures)}."
            )

        return redirect(obj)
