# Generated by Django 4.0.5 on 2022-07-01 22:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0107_rename__note_note_notes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="time",
            name="invoice",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.invoice",
            ),
        ),
    ]
