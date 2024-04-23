from django.apps import apps
from django.http import HttpResponseRedirect


def archive(request):
    archive = request.GET.get("archive", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    obj = None
    if model == "user":
        ModelClass = apps.get_model(app_label="siteuser", model_name="User")
        archive_field = "is_active"
    else:
        ModelClass = apps.get_model(app_label="db", model_name=model.capitalize())
        archive_field = "archived"
    field_value = False if archive == "false" else True
    obj = ModelClass.objects.get(id=obj_id)
    if model == "user":
        field_value = not (field_value)
    setattr(obj, archive_field, field_value)
    if model == "invoice":
        for time_entry in obj.times.all():
            setattr(time_entry, archive_field, field_value)
            time_entry.save()

    if obj:
        obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))
