from django.http import HttpResponseRedirect


def display_mode(request):
    mode = request.GET.get("display-mode", "dark")
    if mode == "light":
        request.user.profile.dark = False
        request.user.profile.save()
    elif mode == "dark":
        request.user.profile.dark = True
        request.user.profile.save()
    return HttpResponseRedirect(request.headers.get("Referer"))
