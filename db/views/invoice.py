import io
import locale
from itertools import chain

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import get_template
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
from docx import Document
from faker import Faker
from html2docx import html2docx
from texttable import Texttable
from xhtml2pdf import pisa

from ..forms.invoice import InvoiceForm, TimeFormSet
from ..forms.time import TimeForm
from ..models.invoice import Invoice
from ..models.project import Project
from ..models.time import Time
from .base import BaseView

fake = Faker()


class BaseInvoiceView(BaseView, UserPassesTestMixin):
    model = Invoice
    model_name = model._meta.model_name
    model_name_plural = model._meta.verbose_name_plural
    form_model = InvoiceForm
    form_class = InvoiceForm
    url_cancel = f"{model_name.lower()}_cancel"
    url_copy = f"{model_name.lower()}_copy"
    url_create = f"{model_name.lower()}_create"
    url_delete = f"{model_name.lower()}_delete"
    url_edit = f"{model_name.lower()}_edit"
    url_index = f"{model_name.lower()}_index"
    url_view = f"{model_name.lower()}_view"
    template_name = "edit.html"
    exclude = [
        "contacts",
        "company",
        "start_date",
        "end_date",
        "due_date",
        "user",
        "client",
        "project",
        "task",
        "issue_date",
    ]

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    @staticmethod
    def generate_docx(html_content, title):
        docx_content = html2docx(html_content, title=title)
        doc = Document(docx_content)
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer


class InvoiceListView(BaseInvoiceView, ListView):
    model = Invoice
    template_name = "index.html"


class InvoiceCreateView(BaseInvoiceView, CreateView):
    success_url = reverse_lazy("invoice_view")

    def get_success_url(self):
        return reverse_lazy("invoice_view", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_id = self.request.GET.get("project_id")
        doc_type = self.request.GET.get("doc-type")
        now = timezone.now()

        # Get month and year
        year = now.year
        month = now.month

        # Get start and end date
        start_date = timezone.datetime(year, month, 1)
        end_date = (
            timezone.datetime(year, month, 1) + timezone.timedelta(days=32)
        ).replace(day=1) - timezone.timedelta(days=1)

        # Get due date
        month = now.month + 2
        if month > 12:
            year += 1
            month -= 12
        due_date = timezone.datetime(year, month, 1)

        # Get issue date
        month = now.month + 1
        if month > 12:
            year += 1
            month -= 12
        if month == 12:
            year += 1
            month = 1
        issue_date = timezone.datetime(year, month, 1)

        # Set initial context
        context["form"].initial = {
            "start_date": start_date,
            "end_date": end_date,
            "issue_date": issue_date,
            "due_date": due_date,
        }

        # Update context to include project and client
        if project_id:
            project = Project.objects.get(pk=project_id)
            client = project.client
            company = None
            if client:
                company = client.company
            task = project.task
            subject = f"{project} {now.strftime('%B %Y')}"
            context["form"].initial.update(
                {
                    "subject": subject,
                    "client": client,
                    "project": project,
                    "company": company,
                    "task": task,
                }
            )

        # Update context to include doc_type
        if doc_type:
            context["form"].initial.update(
                {
                    "doc_type": doc_type,
                }
            )

        # Update context to include fake text
        subject = None
        if settings.USE_FAKE:
            subject = fake.text()
            context["form"].initial.update(
                {
                    "subject": subject,
                }
            )

        # extra = self.request.GET.get("extra")
        # if extra:
        #     extra = int(extra)
        # else:
        #     extra = 1
        # time = self.request.GET.get("time")
        # if time and time == "1":
        #     extra += 1
        # elif time and time == "0":
        #     extra -= 1
        # context["extra"] = extra
        # start_date = timezone.now()
        # if self.request.POST:
        #     time_formset = TimeFormSet(
        #         self.request.POST, instance=self.object, prefix="time"
        #     )
        # else:
        #     initial_data = [
        #         {
        #             "user": self.request.user,
        #             "date": start_date + timezone.timedelta(days=_),
        #             "description": fake.text(),
        #         }
        #         for _ in range(20)
        #     ]
        #     time_formset = TimeFormSet(
        #         instance=self.object, prefix="time", initial=initial_data
        #     )
        #     time_formset.extra = extra
        # context["time_formset"] = time_formset
        # context["time_formset_helper"] = TimeForm().helper
        # context["url_create_formset"] = "%s_create" % self.model_name

        return context

    def form_valid(self, form):
        self.object = form.save()
        project_id = self.request.GET.get("project_id")
        if project_id:
            project = Project.objects.get(pk=project_id)
            self.object.project = project
            self.object.save()
        return super().form_valid(form)


class InvoiceDetailView(BaseInvoiceView, DetailView):
    url_export_doc = "invoice_export_doc"
    url_export_pdf = "invoice_export_pdf"
    url_email_doc = "invoice_email_doc"
    url_email_pdf = "invoice_email_pdf"
    url_email_text = "invoice_email_text"
    template_name = "view.html"

    def get_context_data(self, **kwargs):
        invoice = self.get_object()
        contacts = invoice.contacts.all()
        notes = invoice.notes.all()
        times = invoice.times.all().order_by("date")
        project = invoice.project
        client = invoice.client
        task = invoice.task
        queryset_related = [q for q in [notes, times, contacts] if q.exists()]
        if project:
            queryset_related.append([project])
        if client:
            queryset_related.append([client])
        if task:
            queryset_related.append([task])
        queryset_related = list(chain(*queryset_related))
        queryset_related = sorted(queryset_related, key=self.get_archived)
        self.queryset_related = queryset_related
        self.has_related = True
        context = super().get_context_data(**kwargs)

        context["times"] = times
        context["notes"] = notes
        context["url_export_doc"] = self.url_export_doc
        context["url_export_pdf"] = self.url_export_pdf
        context["url_email_doc"] = self.url_email_doc
        context["url_email_pdf"] = self.url_email_pdf
        context["url_email_text"] = self.url_email_text
        if self.object.doc_type in settings.DOC_TYPES:
            context["doc_type"] = settings.DOC_TYPES[self.object.doc_type]
        return context


class InvoiceUpdateView(BaseInvoiceView, UpdateView):
    template_name = "edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["url_cancel"] = f"{self.model_name}_view"
        context["pk"] = self.kwargs["pk"]
        extra = self.request.GET.get("extra")
        if extra:
            extra = int(extra)
        else:
            extra = 1
        time = self.request.GET.get("time")
        if time and time == "1":
            extra += 1
        elif time and time == "0":
            extra -= 1
        context["extra"] = extra
        if self.request.POST:
            time_formset = TimeFormSet(self.request.POST, instance=self.object)
        else:
            time_formset = TimeFormSet(
                instance=self.object, queryset=Time.objects.order_by("date")
            )
            time_formset.extra = extra
        context["time_formset"] = time_formset
        context["time_formset_helper"] = TimeForm().helper
        context["url_create_formset"] = "%s_create" % self.model_name
        return context

    def get_initial(self):
        initial = super().get_initial()
        times = Time.objects.filter(invoice=self.object)
        initial_times = [time.id for time in times]
        initial["times"] = initial_times
        return initial

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(pk=self.kwargs["pk"])

    def get_success_url(self):
        return reverse_lazy("invoice_view", args=[self.object.pk])

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class InvoiceDeleteView(BaseInvoiceView, DeleteView):
    model = Invoice
    form_model = InvoiceForm
    success_url = reverse_lazy("invoice_index")
    template_name = "delete.html"

    def get_queryset(self):
        return Invoice.objects.all()


class InvoiceCopyView(BaseInvoiceView, CreateView):
    model = Invoice
    form_model = InvoiceForm
    success_url = reverse_lazy("invoice_index")

    def get_queryset(self):
        return Invoice.objects.all()

    def get_initial(self):
        original_invoice = Invoice.objects.get(pk=self.kwargs["pk"])
        return {
            "name": original_invoice.name,
        }

    def form_valid(self, form):
        new_invoice = form.save(commit=False)
        new_invoice.pk = None
        new_invoice.save()
        return super().form_valid(form)


class InvoiceExportDOCView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        doc_type = settings.DOC_TYPES[obj.doc_type]
        context["doc_type"] = doc_type
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        subject = obj.subject
        buffer = self.generate_docx(html_content, title=subject)
        response = FileResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model_name}_{object_id}.docx"'
        )
        return response


class InvoiceExportPDFView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        context["doc_type"] = settings.DOC_TYPES[obj.doc_type]
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        template = get_template(self.template_name)
        html_content = template.render(context)
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), pdf_file)
        pdf_file.seek(0)
        response = FileResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="{self.model_name}_{object_id}.pdf"'
        )

        return response


class InvoiceEmailDOCView(BaseInvoiceView, View):
    model = Invoice
    template_name = None

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        doc_type = settings.DOC_TYPES[obj.doc_type]
        context["doc_type"] = doc_type
        template = get_template(self.template_name)
        html_content = template.render(context)
        subject = obj.subject
        buffer = self.generate_docx(html_content, title=subject)
        contact_emails = [
            contact.email for contact in obj.contacts.all() if contact.email is not None
        ]
        if contact_emails:
            for contact_email in contact_emails:
                email = EmailMessage(
                    subject=subject,
                    body="Please find attached, thank you!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact_email],
                )
                email.attach(
                    f"{subject.replace(' ', '_')}.docx",
                    buffer.getvalue(),
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email = EmailMessage(
                subject=subject,
                body="Please find attached, thank you!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
            )
            email.attach(
                f"{subject.replace(' ', '_')}.docx",
                buffer.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)


class InvoiceEmailPDFView(BaseInvoiceView, View):
    model = Invoice
    template_name = None

    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        self.template_name = "table/invoice.html"
        context = {}
        context["pdf"] = True
        context["object"] = obj
        context["times"] = obj.times.all().order_by("date")
        context["doc_type"] = settings.DOC_TYPES[obj.doc_type]
        template = get_template(self.template_name)
        html_content = template.render(context)
        pdf_file = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), pdf_file)
        pdf_file.seek(0)
        subject = obj.subject
        contact_emails = [
            contact.email for contact in obj.contacts.all() if contact.email is not None
        ]
        if contact_emails:
            for contact_email in contact_emails:
                email = EmailMessage(
                    subject=subject,
                    body="Please find attached, thank you!",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[contact_email],
                )
                email.attach(
                    f"{subject.replace(' ', '_')}.pdf",
                    pdf_file.getvalue(),
                    "application/pdf",
                )
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email = EmailMessage(
                subject=subject,
                body="Please find attached, thank you!",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.DEFAULT_FROM_EMAIL],
            )
            email.attach(
                f"{subject.replace(' ', '_')}.pdf",
                pdf_file.getvalue(),
                "application/pdf",
            )
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)


class InvoiceEmailTextView(BaseInvoiceView, View):
    def get(self, request, *args, **kwargs):
        object_id = self.kwargs["object_id"]
        obj = get_object_or_404(self.model, id=object_id)
        now = timezone.now()
        subject = obj.subject
        doc_type = settings.DOC_TYPES[obj.doc_type]
        text_content = f"{doc_type.upper()}\n\n"
        body = ""
        contact_emails = [
            contact.email for contact in obj.contacts.all() if contact.email is not None
        ]
        header = Texttable()
        header.set_deco(Texttable.VLINES)
        header.set_cols_align(["r", "l", "r", "l"])
        header.add_rows(
            [
                ["", "", "", ""],
                ["Id:", obj.id, "From:", obj.company or "Some company"],
                ["", "", "", ""],
                [
                    "Issue Date:",
                    f"{obj.issue_date.strftime('%B %d, %Y')}" or "",
                    "",
                    "",
                ],
                [
                    "Due Date:",
                    f"{obj.due_date.strftime('%B %d, %Y')}" if obj.due_date else "",
                    "For:",
                    (
                        f"{obj.client}\n{obj.client.address}"
                        if obj.client and obj.client.address
                        else ""
                    )
                    or (
                        f"{obj.user.first_name} {obj.user.last_name}\n{obj.user.profile.address}"
                        if obj.user and obj.user.profile.address
                        else ""
                    ),
                ]
                if obj.due_date or obj.client
                else ["", "", "", ""],
                ["Subject:", subject, "", ""],
                ["", "", "", ""],
                [
                    "Period of\nperformance",
                    f"{obj.start_date.strftime('%B %d, %Y')} - {obj.end_date.strftime('%B %d, %Y')}",
                    "",
                    "",
                ],
                ["", "", "", ""],
            ]
        )
        text_content += f"{header.draw()}\n\n"
        table = Texttable()
        table.add_row(
            ["Date", "Task", "Description", "Quantity", "Unit Price", "Amount"]
        )
        total = {}
        total["amount"] = 0
        total["hours"] = 0
        total["rate"] = obj.project.task.rate
        for entry in obj.times.all():
            rate = 0
            amount = entry.amount
            hours = entry.hours
            if entry.project:
                if entry.project.task:
                    rate = entry.project.task.rate
            if obj.doc_type == "task-order":
                rate = entry.user.profile.rate
                total["rate"] = rate
                amount = rate * hours
            total["amount"] += amount
            total["hours"] += hours
        table.add_row(
            ["Total", "", "", "", "", locale.currency(total["amount"], grouping=True)]
        )
        text_content += f"{table.draw()}\n\n"
        notes = obj.notes.all()
        if notes:
            text_content += "Notes\n\n"
            for note in notes:
                text_content += f"- {note}\n\n"
        html_content = f"<pre>{text_content}</pre>"
        subject = obj.subject
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
        )
        email.attach_alternative(html_content, "text/html")
        if contact_emails:
            for contact_email in contact_emails:
                email.to = [contact_email]
                email.send()
                messages.success(
                    request, f"Email sent successfully to: {contact_email}"
                )
        else:
            email.to = [settings.DEFAULT_FROM_EMAIL]
            email.send()
            messages.success(
                request, f"Email sent successfully to: {settings.DEFAULT_FROM_EMAIL}"
            )
        return redirect(obj)
