# Create your views here.

from .models import ResumePage


def export_to_pdf(request, page_id):
    return ResumePage.export_to_pdf(page_id)


def export_to_md(request, page_id):
    return ResumePage.export_to_md(page_id)


def export_to_docx(request, page_id):
    return ResumePage.export_to_docx(page_id)
