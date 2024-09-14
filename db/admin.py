from decimal import Decimal

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from import_export import fields, widgets
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource as ImportExportModelResource

from .models.client import Client
from .models.company import Company
from .models.contact import Contact
from .models.invoice import Invoice
from .models.note import Note
from .models.profile import Profile
from .models.project import Project
from .models.report import Report
from .models.task import Task
from .models.testimonial import Testimonial
from .models.time import Time
from .models.time import TimeEntry


@admin.register(Testimonial)
class TestimonialAdmin(ImportExportModelAdmin):
    pass


def item_inactive(modeladmin, request, queryset):
    queryset.update(archived=True)


item_inactive.short_description = "Selected items inactive"


class BooleanWidget(widgets.Widget):
    def clean(self, value):
        """
        Return eval string value
        """
        if value == "Yes":
            return True
        else:
            return False


class DecimalWidget(widgets.Widget):
    def clean(self, value):
        """
        Return eval string value
        """
        if value:
            return Decimal(value.replace(",", ""))
        else:
            return Decimal(0)


class UserWidget(widgets.Widget):
    def clean(self, value):
        return value


class ClientResource(ImportExportModelResource):
    class Meta:
        model = Client

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    resource_class = ClientResource


@admin.register(Company)
class CompanyAdmin(ImportExportModelAdmin):
    pass


class ContactResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )

    class Meta:
        model = Contact

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Contact)
class ContactAdmin(ImportExportModelAdmin):
    resource_class = ContactResource


class InvoiceResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )
    amount = fields.Field(
        column_name="amount", attribute="amount", widget=DecimalWidget()
    )
    paid_amount = fields.Field(
        column_name="paid_amount", attribute="paid_amount", widget=DecimalWidget()
    )
    subtotal = fields.Field(
        column_name="subtotal", attribute="subtotal", widget=DecimalWidget()
    )
    balance = fields.Field(
        column_name="balance", attribute="balance", widget=DecimalWidget()
    )
    document_id = fields.Field(
        column_name="invoice_id", attribute="document_id", widget=DecimalWidget()
    )

    class Meta:
        model = Invoice

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceResource
    actions = [item_inactive]


@admin.register(Note)
class NoteAdmin(ImportExportModelAdmin):
    actions = [item_inactive]


class ProjectResource(ImportExportModelResource):
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )
    billable_amount = fields.Field(
        column_name="billable_amount",
        attribute="billable_amount",
        widget=DecimalWidget(),
    )
    budget = fields.Field(
        column_name="budget", attribute="budget", widget=DecimalWidget()
    )
    budget_spent = fields.Field(
        column_name="budget_spent", attribute="budget_spent", widget=DecimalWidget()
    )
    team_costs = fields.Field(
        column_name="team_costs", attribute="team_costs", widget=DecimalWidget()
    )
    total_costs = fields.Field(
        column_name="total_costs", attribute="total_costs", widget=DecimalWidget()
    )

    class Meta:
        model = Project
        exclude = ("task", "team")

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Profile)
class ProfileAdmin(ImportExportModelAdmin):
    list_display = ("__str__", "archived", "user")


@admin.register(Project)
class ProjectAdmin(ImportExportModelAdmin):
    resource_class = ProjectResource


@admin.register(Report)
class ReportAdmin(ImportExportModelAdmin):
    actions = [item_inactive]


class TaskResource(ImportExportModelResource):
    class Meta:
        model = Task
        exclude = ("unit", "billable", "archived")

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Task)
class TaskAdmin(ImportExportModelAdmin):
    resource_class = TaskResource


class TimeResource(ImportExportModelResource):
    billable = fields.Field(
        column_name="billable", attribute="billable", widget=BooleanWidget()
    )
    client = fields.Field(
        column_name="client",
        attribute="client",
        widget=widgets.ForeignKeyWidget(Client, "name"),
    )
    invoiced = fields.Field(
        column_name="invoiced", attribute="invoiced", widget=BooleanWidget()
    )
    project = fields.Field(
        column_name="project",
        attribute="project",
        widget=widgets.ForeignKeyWidget(Project, "name"),
    )
    task = fields.Field(
        column_name="task",
        attribute="task",
        widget=widgets.ForeignKeyWidget(Task, "name"),
    )
    user = fields.Field(column_name="user", attribute="user", widget=UserWidget())

    class Meta:
        model = Time

    def get_instance(self, instance_loaders, row):
        return False

    def before_import(self, dataset, dry_run, file_name=None, user=None):
        if dataset.headers:
            dataset.headers = [
                str(header).lower().strip() for header in dataset.headers
            ]

        if "id" not in dataset.headers:
            dataset.headers.append("id")


@admin.register(Time)
class TimeAdmin(ImportExportModelAdmin):
    resource_class = TimeResource
    actions = [item_inactive]


# Define and reregister a custom UserAdmin class
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(TimeEntry)
class TimeAdmin(admin.ModelAdmin):
    """ """
