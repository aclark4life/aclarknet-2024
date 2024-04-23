from django.db.models import BooleanField, Case, Value, When
from django.core.paginator import Paginator
from django.conf import settings

archived_annotation = Case(
    When(is_active=False, then=Value(True)),
    default=Value(False),
    output_field=BooleanField(),
)


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
    search = False
    dashboard = False
    exclude = ["contacts"]

    def get_archived(self, obj):
        try:
            return obj.archived
        except:
            return not obj.is_active

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.model_name:
            context["model_name"] = self.model_name

        if self.model_name_plural:
            context["model_name_plural"] = self.model_name_plural

        context["statcards"] = {}
        context["statcard"] = self.get_context_statcards()
        context["urls"] = self.get_context_urls()

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

        if self.has_related:
            if len(self.queryset_related) > 0:
                context["has_related"] = True
                queryset = self.queryset_related

        paginator = Paginator(queryset, per_page)
        if self.paginated:
            page_obj = paginator.get_page(page_number)
        else:
            page_obj = queryset
        context["page_obj"] = page_obj

        if hasattr(self, "form_class"):
            context["page_obj_field_values"] = self.get_context_page_obj_field_values(
                page_obj
            )
        if self.model and hasattr(self, "object"):
            context["page_obj_detail"] = self.get_context_page_obj_detail()
        if hasattr(self, "form_class") and hasattr(self, "object"):
            object = self.object
            object_fields = self.form_class().fields.keys()
            try:
                object_field_values = [
                    (field_name, getattr(object, field_name))
                    for field_name in object_fields
                    if field_name not in self.exclude
                ]
            except AttributeError:
                object_field_values = []
            context["object_field_values"] = object_field_values
        context[f"{self.model_name}_nav"] = True
        return context

    def get_context_page_obj_field_values(self, page_obj):
        page_obj_field_values = []
        page_obj_field_items = self.form_class().fields.items()
        for item in page_obj:
            object_field_values = []
            object_field_values.append(("type", item._meta.model_name))
            object_field_values.append(("id", item.id))
            for field_name, field in page_obj_field_items:
                if field_name not in self.exclude:
                    try:
                        object_field_values.append(
                            (field_name, getattr(item, field_name))
                        )
                    except AttributeError:
                        object_field_values.append((field_name, ""))
            page_obj_field_values.append(object_field_values)
        return page_obj_field_values

    def get_context_page_obj_detail(self):
        context = {}
        first_object = None
        last_object = None
        next_object = None
        previous_object = None
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

    def get_context_statcards(self):
        context = {}

        context["times"] = {}
        context["invoices"] = {}

        context["times"]["entered"] = 0
        context["times"]["approved"] = 0
        context["invoices"]["gross"] = 0
        context["invoices"]["cost"] = 0
        context["invoices"]["net"] = 0

        return context

    def get_context_urls(self):
        context = {}

        context["url_cancel"] = self.url_cancel
        context["url_copy"] = self.url_copy
        context["url_create"] = self.url_create
        context["url_delete"] = self.url_delete
        context["url_edit"] = self.url_edit
        context["url_index"] = self.url_index
        context["url_view"] = self.url_view

        return context
