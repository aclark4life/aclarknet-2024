from django.db import connection, migrations


def drop_table(apps, schema_editor, table_name):
    if table_exists(table_name):
        sql = f"DROP TABLE {table_name};"
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(sql)
    else:
        print(f"The table '{table_name}' does not exist.")


def table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = %s
            )
            """,
            [table_name],
        )
        return cursor.fetchone()[0]


class Migration(migrations.Migration):
    dependencies = [
        ("db", "0120_alter_time_client_alter_time_project_alter_time_task"),
    ]

    operations = [
        migrations.RunPython(
            lambda apps, schema_editor: drop_table(apps, schema_editor, "home_homepage")
        ),
        migrations.RunPython(
            lambda apps, schema_editor: drop_table(apps, schema_editor, "root_homepage")
        ),
        migrations.RunPython(
            lambda apps, schema_editor: drop_table(
                apps, schema_editor, "basicpage_basicpage"
            )
        ),
        migrations.RunPython(
            lambda apps, schema_editor: drop_table(
                apps, schema_editor, "testimonial_testimonialpage"
            )
        ),
    ]
