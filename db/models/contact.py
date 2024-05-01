from uuid import uuid4
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from db.models.base import BaseModel
from db.models.client import Client
from django.shortcuts import reverse


class Contact(BaseModel):
    """
    Client, First Name, Last Name, Title, Email, Office Phone, Mobile Phone,
    Fax
    """

    client = models.ForeignKey(Client, blank=True, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=300, blank=True, null=True)
    last_name = models.CharField(max_length=300, blank=True, null=True)
    email = models.EmailField("E-Mail Address", blank=True, null=True)
    mobile_phone = PhoneNumberField("Mobile Phone", blank=True, null=True)
    office_phone = PhoneNumberField("Office Phone", blank=True, null=True)
    phone = models.CharField(max_length=300, blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    uuid = models.UUIDField("UUID", max_length=300, default=uuid4)
    number = models.CharField(max_length=300, blank=True, null=True)
    url = models.URLField("URL", max_length=300, blank=True, null=True)

    def get_absolute_url(self):
        return reverse("contact_view", args=[str(self.id)])

    def save(self, *args, **kwargs):
        if not self.name:
            if self.first_name and self.last_name:
                self.name = f"{self.first_name} {self.last_name}"
        super().save(*args, **kwargs)
