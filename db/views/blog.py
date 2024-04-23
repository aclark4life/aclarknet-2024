from django.http import HttpResponseRedirect


def blog(request):
    return HttpResponseRedirect("https://blog.aclark.net")
