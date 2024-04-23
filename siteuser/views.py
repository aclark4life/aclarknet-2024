import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

# from .models import User
from django.contrib.auth.models import User
from .forms import SiteUserForm


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "profile.html"

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator(csrf_exempt, name="dispatch")
class UpdateThemePreferenceView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode("utf-8"))
            new_theme = data.get("theme")
            user = request.user
            profile = user.profile
            profile.user_theme_preference = new_theme
            profile.save()
            response_data = {"theme": new_theme}
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            return JsonResponse({"error": e}, status=400)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return JsonResponse({"error": "Invalid request method"}, status=405)


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "user_edit.html"  # Create this template in your templates folder
    form_class = SiteUserForm

    def get_success_url(self):
        return reverse_lazy("user-profile")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"].initial = {"rate": self.object.profile.rate}
        return context
