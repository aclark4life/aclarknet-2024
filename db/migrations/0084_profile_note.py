# Generated by Django 3.1.4 on 2021-01-26 21:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0083_auto_20210124_2252")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="note",
            field=models.ManyToManyField(blank=True, to="db.Note"),
        )
    ]