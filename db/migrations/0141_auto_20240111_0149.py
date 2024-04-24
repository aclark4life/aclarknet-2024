# Generated by Django 5.0 on 2024-01-11 01:49

from django.db import migrations


def move_leads_to_contacts(apps, schema_editor):
    Lead = apps.get_model("db", "Lead")
    Contact = apps.get_model("db", "Contact")

    # Move Lead objects to Contact objects
    for lead in Lead.objects.all():
        contact = Contact(name=lead.name, url=lead.url, number=lead.number)
        contact.save()
    Lead.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        # Add your app dependencies here
        ("db", "0140_contact_number_contact_url"),
    ]

    operations = [
        migrations.RunPython(move_leads_to_contacts),
    ]
