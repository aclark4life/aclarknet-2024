# Generated by Django 5.0.3 on 2024-03-30 19:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("modelformtest", "0002_marketingemailmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="testmodel",
            name="is_subscribed",
            field=models.BooleanField(default=True),
        ),
    ]