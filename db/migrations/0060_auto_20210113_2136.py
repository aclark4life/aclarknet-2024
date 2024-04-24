# Generated by Django 3.1.4 on 2021-01-13 21:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0059_auto_20210113_1046")]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="task",
            field=models.OneToOneField(
                blank=True,
                limit_choices_to={"active": True},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.task",
            ),
        )
    ]
