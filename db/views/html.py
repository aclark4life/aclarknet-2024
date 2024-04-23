from django.apps import apps
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404


def html_mode(request):
    html = request.GET.get("html", "true")
    model = request.GET.get("model")
    obj_id = request.GET.get("id")
    html = False if html.lower() == "false" else True
    ModelClass = apps.get_model(app_label="db", model_name=model.capitalize())
    obj = get_object_or_404(ModelClass, pk=obj_id)
    if html:
        obj.html = True
    else:
        obj.html = False
    obj.save()
    return HttpResponseRedirect(request.headers.get("Referer"))
