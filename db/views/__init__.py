from django.shortcuts import render
from django.views.defaults import permission_denied


def custom_403(request, exception=None):
    return permission_denied(request, exception=exception, template_name="403.html")


def custom_404(request, exception=None):
    return render(request, exception=exception, template_name="404.html")


def custom_500(request, exception=None):
    return render(request, exception=exception, template_name="500.html")


def trigger_500(request):
    raise Exception("This is a deliberate 500 error.")
