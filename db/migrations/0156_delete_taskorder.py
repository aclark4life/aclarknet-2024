# Generated by Django 5.1 on 2024-10-06 18:24

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0155_invoice_reset"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TaskOrder",
        ),
    ]
