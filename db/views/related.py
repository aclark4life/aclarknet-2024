from django.apps import apps
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import reverse


def update_related_entries(request):
    if request.method == "POST":
        entry_ids = request.POST.getlist("entry_id")
        if not entry_ids:
            messages.error(request, "No entries selected.")
            return HttpResponseRedirect(reverse("dashboard"))

        summary_message = ""

        for entry_id in entry_ids:
            try:
                model_name, pk = entry_id.split("-")
            except ValueError:
                messages.error(request, "Invalid entry ID format.")
                return HttpResponseRedirect(reverse("dashboard"))

            if model_name == "user":
                ModelClass = apps.get_model(app_label="auth", model_name="User")
            else:
                try:
                    ModelClass = apps.get_model(
                        app_label="db", model_name=model_name.capitalize()
                    )
                except LookupError:
                    messages.error(request, f"Invalid model name: {model_name}")
                    return HttpResponseRedirect(reverse("dashboard"))

            try:
                entry = ModelClass.objects.get(pk=pk)
            except ModelClass.DoesNotExist:
                messages.error(
                    request, f"{model_name.capitalize()} entry not found: {entry_id}"
                )
                return HttpResponseRedirect(reverse(f"{model_name}_index"))

            action = request.POST.get("action")
            if action == "delete":
                try:
                    entry.delete()
                    summary_message += (
                        f"Successfully deleted {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to delete {model_name} entry {entry_id}: {str(e)}",
                    )
            elif action == "archive":
                if model_name == "user":
                    entry.is_active = False
                else:
                    entry.archived = True
                entry.save()
                summary_message += (
                    f"Successfully archived {model_name} entry: {entry_id}\n"
                )
            elif action == "unarchive":
                if model_name == "user":
                    entry.is_active = True
                else:
                    entry.archived = False
                entry.save()
                summary_message += (
                    f"Successfully unarchived {model_name} entry: {entry_id}\n"
                )
            elif action == "html":
                if model_name == "note":
                    entry.html = True
                    entry.save()
                    summary_message += (
                        f"Successfully HTMLed {model_name} entry: {entry_id}\n"
                    )
                else:
                    messages.error(request, "Invalid action requested.")
            elif action == "unhtml":
                if model_name == "note":
                    entry.html = False
                    entry.save()
                    summary_message += (
                        f"Successfully Un-HTMLed {model_name} entry: {entry_id}\n"
                    )
                else:
                    messages.error(request, "Invalid action requested.")
            elif action == "save":
                try:
                    entry.save()
                    summary_message += (
                        f"Successfully saved {model_name} entry: {entry_id}\n"
                    )
                except Exception as e:
                    messages.error(
                        request,
                        f"Failed to save {model_name} entry {entry_id}: {str(e)}",
                    )
            else:
                messages.error(request, "Invalid action requested.")

        if summary_message:
            messages.success(request, summary_message)

    return HttpResponseRedirect(request.headers.get("Referer"))
