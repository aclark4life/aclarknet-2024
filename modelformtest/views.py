from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DetailView,
    View,
    DeleteView,
)
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse
from django.shortcuts import render
from .forms import MarketingEmailMessageForm
from .forms import TestModelForm
from faker import Faker
from django.urls import reverse_lazy
from .models import TestModel, MarketingEmailMessage
import hashlib
from db.views.base import BaseView


def generate_token(email):
    token = hashlib.sha256(email.encode()).hexdigest()
    return token


def verify_token(email, token):
    generated_token = generate_token(email)
    return token == generated_token


class TestModelBaseView(UserPassesTestMixin, BaseView):
    model = TestModel
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_list"
    url_view = f"{model_name.lower()}_detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modelformtest_nav"] = True
        return context

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class TestModelDeleteView(TestModelBaseView, DeleteView):
    model = TestModel
    success_url = reverse_lazy("test_model_list")
    template_name = "test_model_confirm_delete.html"


class TestModelListView(TestModelBaseView, ListView):
    model = TestModel
    form_class = TestModelForm
    template_name = "index.html"
    context_object_name = "test_models"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["marketing_email_messages"] = MarketingEmailMessage.objects.all()
        return context
        for test_model in context["test_models"]:
            test_model.unsubscribe_token = test_model.unsubscribe_token


class TestModelCreateView(TestModelBaseView, CreateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"

    def get_initial(self):
        fake = Faker()
        return {
            "name": fake.name(),
            "email": fake.email(),
            "age": fake.random_int(min=18, max=100),
        }

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestModelUpdateView(TestModelBaseView, UpdateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"


class TestModelDetailView(TestModelBaseView, DetailView):
    model = TestModel
    template_name = "test_model_detail.html"
    context_object_name = "test_model"


class TestModelSendMarketingEmailView(TestModelBaseView, View):
    def get(self, request, *args, **kwargs):
        test_models = TestModel.objects.all()
        recipients = []
        marketing_email_message = MarketingEmailMessage.objects.first()
        if not marketing_email_message:
            messages.info(request, "No marketing email message found!")
            return HttpResponseRedirect(reverse("testmodel_list"))

        for test_model in test_models:
            subject = marketing_email_message.subject
            sender = settings.DEFAULT_FROM_EMAIL
            email_address = test_model.email
            recipients.append(email_address)
            html_message = render_to_string(
                "marketing_email.html",
                {
                    "test_model": test_model,
                    "message": marketing_email_message.message,
                },
            )

            text_message = strip_tags(html_message)
            email = EmailMultiAlternatives(
                marketing_email_message.subject, text_message, sender, [email_address]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()

        messages.success(
            request, f"Marketing emails sent! {', '.join([i for i in recipients])}"
        )

        return HttpResponseRedirect(reverse("testmodel_list"))


class TestModelCreateMarketingEmailView(TestModelBaseView, CreateView):
    model = MarketingEmailMessage
    form_class = MarketingEmailMessageForm
    template_name = "create_marketing_email_message.html"
    success_url = reverse_lazy("testmodel_list")


class TestModelUpdateMarketingEmailView(TestModelBaseView, UpdateView):
    model = MarketingEmailMessage
    form_class = MarketingEmailMessageForm
    template_name = "update_marketing_email_message.html"
    success_url = reverse_lazy("testmodel_list")


class TestModelDeleteMarketingEmailView(TestModelBaseView, DeleteView):
    model = MarketingEmailMessage
    success_url = reverse_lazy("testmodel_list")
    template_name = "delete_marketing_email_message.html"


# class TestModelUnsubscribeView(UpdateView):
#     model = TestModel
#     template_name = "unsubscribe.html"
#     success_url = reverse_lazy("unsubscribe_success")
#
#     def get_object(self, queryset=None):
#         token = self.kwargs.get("token", None)
#         email = self.kwargs.get("email", None)
#         if not verify_token(email, token):
#             return None
#         queryset = TestModel.objects.filter(email=email)
#         return queryset.first()
#
#     def get_form(self, form_class=None):
#         # Override get_form to include only the is_subscribed field
#         form = super().get_form(form_class)
#         form.fields = ["is_subscribed"]
#         return form
#
#     def form_valid(self, form):
#         form.instance.is_subscribed = False
#         return super().form_valid(form)
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["unsubscribe_email"] = self.kwargs.get("email")
#         return context


def unsubscribe_view(request, email, token):
    test_model = get_object_or_404(TestModel, email=email, unsubscribe_token=token)
    test_model.is_subscribed = False
    test_model.save()
    return HttpResponse(
        "You have been successfully unsubscribed from our mailing list."
    )


def unsubscribe_success(request):
    return render(request, "unsubscribe_success.html")
