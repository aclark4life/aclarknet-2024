import io

from django.http import HttpResponse
from docx import Document
from html2docx import html2docx
from markdown import markdown
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtailmarkdown.fields import MarkdownField
from weasyprint import HTML


class ResumePage(Page):
    """
    A Wagtail Page model for the Resume Page.
    """

    template = "resume_page.html"

    body = MarkdownField()

    content_panels = Page.content_panels + [
        FieldPanel("body", classname="full"),
    ]

    class Meta:
        verbose_name = "Resume Page"

    @classmethod
    def export_to_pdf(cls, page_id):
        try:
            # Fetch the page instance
            page_instance = cls.objects.get(pk=page_id)

            # Retrieve Markdown content
            markdown_content = page_instance.body

            # Convert Markdown to HTML
            html_content = cls.markdown_to_html(markdown_content)

            # Generate PDF
            pdf_content = cls.generate_pdf(html_content)

            # Send PDF as response
            response = HttpResponse(pdf_content, content_type="application/pdf")
            response["Content-Disposition"] = "filename=alex-clark-resume.pdf"
            return response
        except cls.DoesNotExist:
            # Handle page not found
            return HttpResponse("Page not found", status=404)

    @classmethod
    def export_to_md(cls, page_id):
        try:
            # Fetch the page instance
            page_instance = cls.objects.get(pk=page_id)

            # Retrieve Markdown content
            markdown_content = page_instance.body

            # Send PDF as response
            response = HttpResponse(markdown_content, content_type="text/plain")
            response["Content-Disposition"] = "filename=alex-clark-resume.md"
            return response
        except cls.DoesNotExist:
            # Handle page not found
            return HttpResponse("Page not found", status=404)

    @classmethod
    def export_to_docx(cls, page_id):
        try:
            # Fetch the page instance
            page_instance = cls.objects.get(pk=page_id)

            # Convert Markdown to HTML
            markdown_content = page_instance.body
            html_content = cls.markdown_to_html(markdown_content)
            doc_buffer = cls.generate_docx(html_content)

            # Create a response with the appropriate content type
            response = HttpResponse(
                doc_buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )

            # Set the content-disposition header for the browser to prompt the user to download the file
            response["Content-Disposition"] = (
                'attachment; filename="alex-clark-resume.docx"'
            )

            return response

        except cls.DoesNotExist:
            return HttpResponse("Page not found", status=404)

    @staticmethod
    def markdown_to_html(markdown_content):
        return markdown(markdown_content)

    @staticmethod
    def generate_pdf(html_content):
        pdf_content = HTML(string=html_content).write_pdf()
        return pdf_content

    @staticmethod
    def generate_docx(html_content):
        docx_content = html2docx(html_content, title="alexclark-resume.docx")

        doc = Document(docx_content)

        # Save the document to an in-memory buffer
        buffer = io.BytesIO()
        doc.save(buffer)

        # Rewind the buffer to the beginning
        buffer.seek(0)

        return buffer
