from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field
from django import forms

from ..models import Note


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("archived", "html", "text")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "form-inline"
        self.helper.form_tag = False
        self.helper.layout = Div(
            Div(Field("html", css_class=""), css_class="col-sm-12"),
            Div(
                Field("title", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            Div(
                Field("text", css_class="form-control bg-transparent border"),
                css_class="col-sm-12",
            ),
            # Div(Field("notes", css_class="form-control"), css_class="col-sm-12"),
            css_class="row",
        )
