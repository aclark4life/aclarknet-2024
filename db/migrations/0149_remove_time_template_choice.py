# Generated by Django 5.0.1 on 2024-01-20 18:09

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0148_remove_contactpage_page_ptr_delete_contactformfield_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="time",
            name="template_choice",
        ),
    ]
