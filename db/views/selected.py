from django.apps import apps
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse


def update_selected_entries(request):
    if request.method == "POST":
        model_name = request.POST.get("model_name")
        action = request.POST.get("action")

        if not model_name:
            messages.error(request, "Invalid model selected.")
            return HttpResponseRedirect(reverse("dashboard"))

        if model_name == "user":
            from django.contrib.auth.models import User as ModelClass
        else:
            ModelClass = apps.get_model(
                app_label="db", model_name=model_name.capitalize()
            )

        entry_ids = request.POST.getlist("entry_id")
        if not entry_ids:
            messages.error(request, "No entries selected.")
            return HttpResponseRedirect(reverse(f"{model_name}_index"))

        try:
            entries = ModelClass.objects.filter(pk__in=entry_ids)
        except ModelClass.DoesNotExist:
            messages.error(request, f"Selected {model_name} entries not found.")
            return HttpResponseRedirect(reverse(f"{model_name}_index"))

        if action == "delete":
            # try:
            deleted_entries = entries.delete()
            # except:
            #     deleted_entries = []
            if len(deleted_entries) > 0:
                if deleted_entries[0]:
                    if model_name == "report":
                        message = f"Successfully deleted {deleted_entries[1]['db.Report']} {model_name} entries."
                    else:
                        message = f"Successfully deleted {deleted_entries[0]} {model_name} entries."
                    messages.success(request, message)
                else:
                    messages.warning(request, f"No {model_name} entries were deleted.")
            else:
                messages.warning(request, f"No {model_name} entries were deleted.")

        elif action == "archive":
            if model_name == "user":
                entries.update(is_active=False)
            else:
                entries.update(archived=True)
            if model_name == "invoice":
                [i.times.all().update(archived=True) for i in entries]
            messages.success(
                request, f"Successfully archived {len(entry_ids)} {model_name} entries."
            )
        elif action == "unarchive":
            if model_name == "user":
                entries.update(is_active=True)
            else:
                entries.update(archived=False)
            if model_name == "invoice":
                [i.times.all().update(archived=False) for i in entries]
            messages.success(
                request,
                f"Successfully unarchived {len(entry_ids)} {model_name} entries.",
            )
        elif action == "html":
            if model_name == "note":
                entries.update(html=True)
                messages.success(
                    request,
                    f"Successfully HTMLed {len(entry_ids)} {model_name} entries.",
                )
            else:
                messages.error(request, "Invalid action requested.")
        elif action == "unhtml":
            if model_name == "note":
                entries.update(html=False)
                messages.success(
                    request,
                    f"Successfully Un-HTMLed {len(entry_ids)} {model_name} entries.",
                )
            else:
                messages.error(request, "Invalid action requested.")
        elif action == "save":
            [i.save() for i in entries]
            messages.success(
                request,
                f"Successfully saved {len(entry_ids)} {model_name} entries.",
            )
        else:
            messages.error(request, "Invalid action requested.")

    return HttpResponseRedirect(reverse(f"{model_name}_index"))
