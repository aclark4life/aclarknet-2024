# Generated by Django 3.1.7 on 2021-07-17 10:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0100_auto_20210617_1309")]

    operations = [
        migrations.AddField(
            model_name="profile", name="dark", field=models.BooleanField(default=True)
        )
    ]