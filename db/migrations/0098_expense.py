# Generated by Django 3.1.7 on 2021-06-02 19:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("db", "0097_profile_lounge_username")]

    operations = [
        migrations.CreateModel(
            name="Expense",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("updated", models.DateTimeField(auto_now=True)),
                ("active", models.BooleanField(default=True)),
                ("publish", models.BooleanField(default=False)),
                ("name", models.CharField(blank=True, max_length=300, null=True)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=12, null=True
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
