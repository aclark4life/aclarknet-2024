# Generated by Django 5.1 on 2024-10-05 23:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0154_alter_taskorder_table"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="reset",
            field=models.BooleanField(default=False),
        ),
    ]