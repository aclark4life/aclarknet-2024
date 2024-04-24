# Generated by Django 5.0.1 on 2024-01-12 22:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0142_report_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="user_theme_preference",
            field=models.CharField(
                choices=[("light", "Light Theme"), ("dark", "Dark Theme")],
                default="light",
                max_length=10,
            ),
        ),
    ]