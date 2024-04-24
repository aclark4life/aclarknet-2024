# Generated by Django 5.0.3 on 2024-04-20 19:55

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("modelformtest", "0005_testmodel_archived"),
    ]

    operations = [
        migrations.AddField(
            model_name="testmodel",
            name="created",
            field=models.DateTimeField(
                default=django.utils.timezone.now, editable=False
            ),
        ),
        migrations.AddField(
            model_name="testmodel",
            name="updated",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
