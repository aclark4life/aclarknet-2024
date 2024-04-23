import random

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from db.models.blocks import MarketingBlock
from db.models.testimonial import Testimonial


class HomePage(Page):
    template = "home_page.html"  # Create a template for rendering the home page
    marketing_blocks = StreamField(
        [
            ("marketing_block", MarketingBlock()),
        ],
        blank=True,
        null=True,
        use_json_field=True,
    )
    content_panels = Page.content_panels + [
        FieldPanel("marketing_blocks"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["home_nav"] = True

        testimonials = Testimonial.objects.all()
        if testimonials.count() > 0:
            context["testimonial"] = random.choice(testimonials)

        return context

    class Meta:
        verbose_name = "Home Page"
