import ast
import locale
import decimal
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from faker import Faker
from texttable import Texttable

from ..forms.report import AdminReportForm, ReportForm

from ..models.note import    Note
from ..models.client import    Client
from ..models.company import    Company
from ..models.contact import    Contact
from ..models.invoice import    Invoice
from ..models.project import    Project
from ..models.report import    Report
from ..models.task import    Task
from ..models.time import    Time

from .base import BaseView

fake = Faker()

locale.setlocale(locale.LC_ALL, "")


class BaseReportView(BaseView, UserPassesTestMixin):
    model = Report
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = ReportForm
    form_class = ReportForm
    template_name = "edit.html"
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    exclude = [
        "date",
        "hours",
        "amount",
        "cost",
        "net",
        "clients",
        "invoices",
        "projects",
        "tasks",
        "contacts",
        "user",
        "company",
        "team",
    ]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied


class CreateOrUpdateReportView(BaseReportView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        last_month = now - timezone.timedelta(days=now.day)
        last_month = last_month.strftime("%B")

        context["form"].initial = {
            "name": f"{last_month} {now.year}",
        }

        clients = Client.objects.filter(archived=False)
        invoices = Invoice.objects.filter(archived=False)
        projects = [invoice.project for invoice in invoices if invoice.project]
        tasks = [project.task for project in projects]
        companies = Company.objects.filter(archived=False)

        # contacts = self.get_object().contacts.all()

        report_hours = invoices.aggregate(hours=Sum("hours"))["hours"]
        report_amount = invoices.aggregate(amount=Sum(F("amount")))["amount"]
        report_cost = invoices.aggregate(cost=Sum(F("cost")))["cost"]
        report_net = invoices.aggregate(net=Sum(F("net")))["net"]

        team = {}
        for project in projects:
            team[project.name] = {}
            task = project.task

            gross, cost, net, rate = 0, 0, 0, 0

            for member in project.team.all():
                times = Time.objects.filter(
                    user=member, project=project, archived=False
                )

                approved = times.filter(invoice__isnull=False).aggregate(
                    total=Sum(F("hours"))
                )
                approved = approved["total"] or 0
                approved = decimal.Decimal(approved)

                if task:
                    gross = approved * task.rate

                profile = member.profile

                if profile:
                    rate = member.profile.rate
                    if rate:
                        cost = approved * member.profile.rate
                    if gross and cost:
                        net = gross - cost

                team[project.name][member.username] = {}
                team[project.name][member.username]["rate"] = str(rate)
                team[project.name][member.username]["hours"] = str(approved)
                team[project.name][member.username]["gross"] = str(gross)
                team[project.name][member.username]["cost"] = str(cost)
                team[project.name][member.username]["net"] = str(net)

            context["statcards"][project.name] = {}
            context["statcards"][project.name]["name"] = project.name
            context["statcards"][project.name]["invoices"] = {}
            context["statcards"][project.name]["invoices"]["gross"] = f"{gross:.2f}"
            context["statcards"][project.name]["invoices"]["cost"] = f"{cost:.2f}"
            context["statcards"][project.name]["invoices"]["net"] = f"{net:.2f}"

            context["form"].initial.update(
                {
                    "clients": clients,
                    # "contacts": contacts,
                    "projects": projects,
                    "tasks": tasks,
                    "invoices": invoices,
                    "hours": f"{report_hours or 0:.2f}",
                    "amount": f"{report_amount or 0:.2f}",
                    "cost": f"{report_cost or 0:.2f}",
                    "net": f"{report_net or 0:.2f}",
                    "user": self.request.user,
                    "company": companies.first(),
                    "team": team,
                }
            )

        return context


class ReportListView(BaseReportView, ListView):
    template_name = "index.html"
    url_export_pdf = "report_export_pdf"
    url_email_pdf = "report_email_pdf"
    url_email_text = "report_email_text"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     if self.request.user.is_superuser:
    #         self.page_obj = self.get_queryset()
    #     elif self.request.user.is_authenticated:
    #         self.page_obj = Report.objects.filter(user=self.request.user)
    #     else:
    #         self.page_obj = Report.objects.none()
    #     context["page_obj"] = self.page_obj
    #     if not self.request.user.is_superuser:
    #         self.exclude_fields.append("Cost")
    #         self.exclude_fields.append("Net")
    #     queryset = Report.objects.filter(archived=False)
    #     hours = queryset.aggregate(total_hours=Sum("hours"))["total_hours"]
    #     hours = hours or 0
    #     hours = f"{hours:.2f}"
    #     hours = {"total": hours}
    #     gross = queryset.aggregate(total_gross=Sum("amount"))["total_gross"]
    #     net = queryset.aggregate(total_net=Sum("net"))["total_net"]
    #     cost = queryset.aggregate(total_cost=Sum("cost"))["total_cost"]

    #     context["statcard"]["invoices"]["gross"] = gross or 0
    #     context["statcard"]["invoices"]["cost"] = cost or 0
    #     context["statcard"]["invoices"]["net"] = net or 0
    #     context["statcard"]["times"]["entered"] = hours
    #     context["statcard"]["times"]["approved"] = hours

    #     context["url_export_pdf"] = self.url_export_pdf
    #     context["url_email_pdf"] = self.url_email_pdf
    #     context["url_email_text"] = self.url_email_text

    #     context["index"] = True

    #     return context

    # def get_queryset(self):
    #     return Report.objects.all().order_by("archived", "-created")


class ReportCreateView(CreateOrUpdateReportView, CreateView):
    success_url = reverse_lazy("report_view")

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminReportForm
        form = super().get_form(form_class)
        form.fields["company"].queryset = Company.objects.filter(archived=False)
        return form

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportDetailView(BaseReportView, DetailView):
    url_export_pdf = "report_export_pdf"
    url_email_pdf = "report_email_pdf"
    url_email_text = "report_email_text"

    def get_context_data(self, **kwargs):
        report = self.get_object()
        company = report.company
        notes = report.notes.all()
        clients = report.clients.all()
        invoices = report.invoices.all()
        projects = report.projects.all()
        contacts = report.contacts.all()
        reports = report.reports.all()
        queryset_related = [
            q
            for q in [clients, contacts, invoices, notes, projects, reports]
            if q.exists()
        ]

        if company:
            queryset_related.insert(0, [company])

        queryset_related = list(chain(*queryset_related))

        for project in projects:
            for team_member in project.team.all():
                if team_member and team_member not in queryset_related:
                    queryset_related.append(team_member)

        for invoice in invoices:
            for time_entry in invoice.times.all():
                if time_entry:
                    queryset_related.append(time_entry)

        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)

        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text

        entered = {"total": report.hours}
        approved = {"total": report.hours}

        context["statcard"]["times"]["entered"] = entered or 0
        context["statcard"]["times"]["approved"] = approved or 0

        context["statcards"]["Report"] = {}
        context["statcards"]["Report"]["name"] = "Report"
        context["statcards"]["Report"]["invoices"] = {}
        context["statcards"]["Report"]["invoices"]["gross"] = report.amount or 0
        context["statcards"]["Report"]["invoices"]["cost"] = report.cost or 0
        context["statcards"]["Report"]["invoices"]["net"] = report.net or 0

        contact_emails = []
        for contact in contacts:
            if contact.email:
                contact_emails.append(contact.email)
        context["contact_emails"] = ", ".join(contact_emails)

        return context

    template_name = "view.html"


class ReportUpdateView(CreateOrUpdateReportView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        return context

    def get_form(self, form_class=None):
        if self.request.user.is_superuser:
            form_class = AdminReportForm
        form = super().get_form(form_class)
        return form

    def get_queryset(self):
        # Retrieve the object to be edited
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("report_view", args=[self.object.pk])


class ReportDeleteView(BaseReportView, DeleteView):
    template_name = "delete.html"
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()


class ReportCopyView(BaseReportView, CreateView):
    success_url = reverse_lazy("report_index")

    def get_queryset(self):
        return Report.objects.all()

    def get_initial(self):
        original_report = Report.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_report.name,
        }

    def form_valid(self, form):
        new_report = form.save(commit=False)
        new_report.pk = None
        new_report.save()
        return super().form_valid(form)


class ReportEmailTextView(BaseReportView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)

        subject = f"{obj.name} Report"

        text_content = f"{self.model_name.upper()}\n\n"

        header = Texttable()
        header.set_deco(Texttable.VLINES)
        header.set_cols_align(["r", "l", "r", "l"])

        net, cost, amount = 0, 0, 0
        if obj.net:
            net = obj.net
        if obj.cost:
            cost = obj.cost
        if obj.amount:
            amount = obj.amount

        contacts = obj.contacts.all()
        header.add_rows(
            [
                ["", "", "", ""],
                ["Id:", obj.id, "Issue Date:", f"{obj.date.strftime('%B %d, %Y')}"],
                ["Name:", obj.name, "From:", obj.company or "Some company"],
                ["Hours:", obj.hours, "Net:", locale.currency(net, grouping=True)],
                [
                    "Gross:",
                    locale.currency(amount, grouping=True),
                    "Cost:",
                    locale.currency(cost, grouping=True),
                ],
                # ["", "", "For:", ", ".join([i.name for i in contacts])]
                ["", "", "", ""] if contacts else ["", "", "", ""],
                ["", "", "", ""],
            ]
        )

        text_content += f"{header.draw()}\n\n"

        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.add_row(
            ["Invoice", "Issue Date", "Hourly Rate", "Hours", "Gross", "Cost", "Net"]
        )

        for invoice in obj.invoices.all():
            rate = 0
            if invoice.project.task:
                rate = invoice.project.task.rate
            table.add_row(
                [
                    invoice.subject,
                    f"{invoice.issue_date.strftime('%B %d, %Y')}",
                    locale.currency(rate, grouping=True),
                    invoice.hours,
                    locale.currency(invoice.amount, grouping=True),
                    locale.currency(invoice.cost, grouping=True),
                    locale.currency(invoice.net, grouping=True),
                ]
            )
            if obj.team:
                for project in obj.team:
                    team_member_data = ast.literal_eval(obj.team[project]).items()
                    if invoice.project.name == project:
                        for field in team_member_data:
                            user = User.objects.get(username=field[0])
                            full_name = "↳ " + " ".join(
                                [user.first_name, user.last_name]
                            )
                            try:
                                table.add_row(
                                    [
                                        full_name or user.username,
                                        "",
                                        locale.currency(float(field[1]["rate"])),
                                        float(field[1]["hours"]),
                                        locale.currency(float(field[1]["gross"])),
                                        locale.currency(float(field[1]["net"])),
                                        locale.currency(float(field[1]["cost"])),
                                    ]
                                )
                            except ValueError:
                                table.add_row(
                                    [
                                        full_name or user.username,
                                        "",
                                        locale.currency(float(0)),
                                        float(field[1]["hours"]),
                                        locale.currency(float(field[1]["gross"])),
                                        locale.currency(float(field[1]["net"])),
                                        locale.currency(float(field[1]["cost"])),
                                    ]
                                )

        text_content += table.draw()

        html_content = f"<pre>{text_content}</pre>"

        contact_emails = [
            contact.email for contact in contacts if contact.email is not None
        ]

        if contact_emails:
            for contact_email in contact_emails:
                email = EmailMultiAlternatives(
                    subject, text_content, settings.DEFAULT_FROM_EMAIL, [contact_email]
                )
                email.attach_alternative(html_content, "text/html")
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)
