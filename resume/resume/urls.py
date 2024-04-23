from django.urls import path
from .views import export_to_pdf, export_to_md, export_to_docx

urlpatterns = [
    path("export-to-pdf/<int:page_id>/", export_to_pdf, name="export-to-pdf"),
    path("export-to-md/<int:page_id>/", export_to_md, name="export-to-md"),
    path("export-to-docx/<int:page_id>/", export_to_docx, name="export-to-docx"),
]
