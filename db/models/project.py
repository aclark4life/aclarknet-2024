from django.db import models
from db.models.base import BaseModel
from db.models.client import Client
from django.conf import settings
from db.models.company import Company


class Project(BaseModel):
    """
    Client, Project, Project Code, Start Date, End Date,
    Total Hours, Billable Hours, Billable Amount, Budget, Budget Spent,
    Budget Remaining, Total Costs, Team Costs, Expenses
    """

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey("Task", blank=True, null=True, on_delete=models.SET_NULL)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    code = models.IntegerField("Project Code", blank=True, null=True)
    total_hours = models.FloatField(blank=True, null=True)
    billable_hours = models.FloatField(blank=True, null=True)
    amount = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    budget = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    budget_spent = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    budget_remaining = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    total_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    team_costs = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    cost = models.DecimalField(blank=True, null=True, max_digits=12, decimal_places=2)
    expenses = models.DecimalField(
        blank=True, null=True, max_digits=12, decimal_places=2
    )
    description = models.TextField(blank=True, null=True)
    po_number = models.CharField("PO Number", max_length=300, blank=True, null=True)
    companies = models.ManyToManyField(Company)
    draggable_positions = models.JSONField(null=True, blank=True)
    github_project = models.CharField(
        "GitHub Project", max_length=300, blank=True, null=True
    )
    github_repository = models.CharField(
        "GitHub Repository", max_length=300, blank=True, null=True
    )

    class Meta:  # https://stackoverflow.com/a/6062320/185820
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse("project_view", args=[str(self.id)])
