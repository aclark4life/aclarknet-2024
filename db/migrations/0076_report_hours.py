# Generated by Django 3.1.4 on 2021-01-21 13:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0075_invoice_hours")]

    operations = [
        migrations.AddField(
            model_name="report",
            name="hours",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=12, null=True
            ),
        )
    ]