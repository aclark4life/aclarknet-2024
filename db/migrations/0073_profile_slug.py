# Generated by Django 3.1.4 on 2021-01-20 01:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0072_auto_20210119_2259")]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="slug",
            field=models.SlugField(blank=True, max_length=150, null=True),
        )
    ]