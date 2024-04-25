from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.views.generic.list import ListView

from ..models.note import Note
from ..models.client import Client
from ..models.company import Company
from ..models.contact import Contact
from ..models.invoice import Invoice
from ..models.profile import Profile
from ..models.project import Project
from ..models.report import Report
from ..models.task import Task
from ..models.time import Time
from .base import BaseView


class SearchView(UserPassesTestMixin, BaseView, ListView):
    template_name = "index.html"
    url_index = "search_index"
    search = True
    context_object_name = "page_obj_field_values"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q")
        context["q"] = query
        return context

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            query_list = query.split()
            queryset = []
            for search_model in [
                Client,
                Company,
                Contact,
                Invoice,
                Note,
                Profile,
                Project,
                Report,
                Task,
                Time,
                User,
            ]:
                q = Q()
                for search_term in query_list:
                    for field in search_model._meta.fields:
                        if (
                            field.__class__.__name__ == "CharField"
                        ):
                            q |= Q(**{f"{field.name}__icontains": search_term})
                if q:
                    queryset += search_model.objects.filter(q)
            return [[('type', 'search'), ('result', queryset)]]


