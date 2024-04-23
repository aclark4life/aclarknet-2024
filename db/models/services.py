from wagtail.models import Page
from db.models.service import Service 


class ServicesPage(Page):
    template = "services_page.html"

    def get_context(self, request):
        context = super().get_context(request)
        services = Service.objects.all()
        context["services"] = services
        return context

    class Meta:
        verbose_name = "Services Page"
