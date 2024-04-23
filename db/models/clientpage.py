from wagtail.models import Page
from django.conf import settings
from db.models.client import Client
from db.models.testimonial import Testimonial


class ClientsPage(Page):
    template = "clients_page.html"

    def get_context(self, request):
        context = super().get_context(request)

        categories = {}

        for tag, category in settings.CLIENT_CATEGORIES.items():
            categories[category] = Client.objects.filter(
                tags__name__in=[tag], publish=True
            )

        context["categories"] = categories

        testimonials = Testimonial.objects.all()
        context["testimonials"] = testimonials

        return context

    class Meta:
        verbose_name = "Clients Page"
