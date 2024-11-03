from django.db.models import BooleanField, Case, Value, When
from django.core.paginator import Paginator
from django.conf import settings
from django.shortcuts import redirect

archived_annotation = Case(
    When(is_active=False, then=Value(True)),
    default=Value(False),
    output_field=BooleanField(),
)


def redirect_admin_to_about_book(request):
    return redirect("/about/#book")


class BaseView:
    model = None
    model_name = None
    model_name_plural = None
    url_cancel = None
    url_copy = None
    url_create = None
    url_delete = None
    url_edit = None
    url_index = None
    url_view = None
    order_by = ["archived", "-created"]
    paginated = False
    page_number = 1
    per_page = settings.PER_PAGE
    queryset_related = []
    has_related = False
    has_preview = False
    search = False
    dashboard = False
    exclude = ["contacts"]

    def get_archived(self, obj):
        try:
            return obj.archived
        except:  # noqa
            return not obj.is_active

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.model_name:
            context["model_name"] = self.model_name
            context[f"{self.model_name}_nav"] = True

        if self.model_name_plural:
            context["model_name_plural"] = self.model_name_plural

        context["statcards"] = {}
        context["statcard"] = self.get_statcards()
        context["urls"] = self.get_urls()

        per_page = self.request.GET.get("items_per_page", settings.PER_PAGE)
        per_page = int(per_page)
        self.per_page = per_page
        context["items_per_page"] = self.per_page

        page_number = self.request.GET.get("page", 1)
        page_number = int(page_number)
        self.page_number = page_number
        context["page_number"] = self.page_number

        paginated = self.request.GET.get("paginated", "true")
        paginated = False if paginated.lower() == "false" else True
        self.paginated = paginated
        context["paginated"] = self.paginated

        queryset = self.get_queryset()
        if queryset and not self.search:
            queryset = queryset.order_by(*self.order_by)

        related = False
        if self.has_related:
            if len(self.queryset_related) > 0:
                context["has_related"] = True
                queryset = self.queryset_related
                related = True

        if self.has_preview:
            context["has_preview"] = True

        paginator = Paginator(queryset, per_page)
        if self.paginated:
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = queryset
        context["page_obj"] = page_obj

        field_values_page = []

        if hasattr(self, "form_class"):
            field_values_page = self.get_field_values(page_obj, related=related)
            context["field_values_page"] = field_values_page

        if hasattr(self, "object") and hasattr(self, "form_class"):
            context["field_values"] = self.get_field_values()

        if hasattr(self, "object") and self.model:
            context["page_obj_detail_view"] = self.get_page_obj_detail_view()

        if self.search:
            context["search"] = self.search
            field_values_page = self.get_field_values(page_obj, search=True)
            if len(field_values_page) > 0:
                context["search_results"] = True
            else:
                context["search_results"] = False
            context["field_values_page"] = field_values_page

        if field_values_page:
            # Table headers via first row
            table_headers = [i[0] for i in field_values_page[0]]
            context["table_headers"] = table_headers

        return context

    def get_field_values(self, page_obj=None, search=False, related=False):
        if page_obj:
            _ = []
            for item in page_obj:
                field_values = []
                if hasattr(page_obj, "object_list"):
                    if page_obj.object_list[0] is not None:
                        field_values.append(("type", item._meta.model_name))
                        field_values.append(("id", item.id))
                        field_values.append(("archived", self.get_archived(item)))
                        field_values.append(("item", item))
                else:
                    field_values.append(("type", item._meta.model_name))
                    field_values.append(("id", item.id))
                    field_values.append(("archived", self.get_archived(item)))
                    field_values.append(("item", item))
                if hasattr(item, "amount"):
                    field_values.append(("amount", item.amount))
                if hasattr(item, "cost"):
                    field_values.append(("cost", item.cost))
                if hasattr(item, "net"):
                    field_values.append(("net", item.net))
                if hasattr(item, "hours"):
                    field_values.append(("hours", item.hours))
                _.append(field_values)
            return _
        else:
            try:
                object_fields = self.form_class().fields.keys()
                field_values = [
                    (field_name, getattr(self.object, field_name))
                    for field_name in object_fields
                    if field_name not in self.exclude
                    and self.request.user.is_superuser()
                ]
            except AttributeError:
                field_values = []
            return field_values

    def get_page_obj_detail_view(self):
        context = {}
        first_object = None
        last_object = None
        next_object = None
        previous_object = None
        if self.request.user.is_authenticated and not self.request.user.is_superuser:
            objects = self.model.objects.filter(user=self.request.user)
        else:
            objects = self.model.objects.all()
        paginator = Paginator(objects, 1)
        page_number = self.request.GET.get("page_number_detail", 1)
        page_number = int(page_number)
        page_obj_detail = paginator.get_page(page_number)
        count = paginator.count
        if page_number:
            current_index = paginator.page(page_number).start_index()
            if current_index < count:
                next_object = objects[current_index]
                last_object = objects[count - 1]
            if current_index > 1:
                previous_object = objects[current_index - 2]
                first_object = objects[0]
        context["next_object"] = next_object
        context["previous_object"] = previous_object
        context["first_object"] = first_object
        context["last_object"] = last_object
        context["count"] = count
        context["page_obj"] = page_obj_detail
        return context

    def get_statcards(self):
        context = {}

        context["times"] = {}
        context["invoices"] = {}

        context["times"]["entered"] = 0
        context["times"]["approved"] = 0
        context["invoices"]["gross"] = 0
        context["invoices"]["cost"] = 0
        context["invoices"]["net"] = 0

        return context

    def get_urls(self):
        context = {}

        context["url_cancel"] = self.url_cancel
        context["url_copy"] = self.url_copy
        context["url_create"] = self.url_create
        context["url_delete"] = self.url_delete
        context["url_edit"] = self.url_edit
        context["url_index"] = self.url_index
        context["url_view"] = self.url_view

        return context
