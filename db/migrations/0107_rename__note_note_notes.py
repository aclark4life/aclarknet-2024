# Generated by Django 3.2.11 on 2022-02-02 14:48

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("db", "0106_report_notes")]

    operations = [
        migrations.RenameField(model_name="note", old_name="_note", new_name="notes")
    ]