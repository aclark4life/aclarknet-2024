from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class NowPage(Page):
    body = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
    ]
