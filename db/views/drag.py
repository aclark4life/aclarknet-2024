from django.http import JsonResponse


def save_positions(request):
    if request.method == "POST":
        profile = request.user.profile
        positions = request.POST.get(
            "positions"
        )  # Assuming positions are sent as form data
        profile.draggable_positions = positions
        profile.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
