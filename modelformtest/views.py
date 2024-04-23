from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .models import TestModel
from .forms import TestModelForm


class TestModelListView(ListView):
    model = TestModel
    template_name = "test_model_list.html"
    context_object_name = "test_models"


class TestModelCreateView(CreateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class TestModelUpdateView(UpdateView):
    model = TestModel
    form_class = TestModelForm
    template_name = "test_model_form.html"


class TestModelDetailView(DetailView):
    model = TestModel
    template_name = "test_model_detail.html"
    context_object_name = "test_model"
