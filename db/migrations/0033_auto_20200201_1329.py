# Generated by Django 2.2.9 on 2020-02-01 13:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0032_auto_20200130_1503")]

    operations = [
        migrations.AlterModelOptions(
            name="statementofwork",
            options={"verbose_name_plural": "Statements of work"},
        ),
        migrations.AddField(
            model_name="time",
            name="task_order",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="db.TaskOrder",
            ),
        ),
    ]
