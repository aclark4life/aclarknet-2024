# Generated by Django 5.0.1 on 2024-01-16 20:29

import django.contrib.postgres.fields.hstore
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0145_delete_expense"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="team",
            field=django.contrib.postgres.fields.hstore.HStoreField(
                blank=True, null=True
            ),
        ),
    ]
