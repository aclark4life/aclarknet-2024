from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from db.models.blocks import MarketingBlock


class AboutPage(Page):
    template = "about_page.html"
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

    class Meta:
        verbose_name = "About Page"
