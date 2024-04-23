from django.http import JsonResponse
from django.views import View
from faker import Faker


class FakeTextView(View):
    def get(self, request, *args, **kwargs):
        fake = Faker()
        fake_data = {"paragraph": [fake.paragraph() for i in range(2)]}
        return JsonResponse(fake_data)
