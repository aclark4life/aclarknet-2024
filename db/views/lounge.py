from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def lounge(request):
    context = {}
    context["lounge_nav"] = True
    return render(request, "lounge.html", context)
