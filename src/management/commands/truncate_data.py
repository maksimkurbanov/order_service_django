from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = "Truncate all tables for the specified app(s)"

    def add_arguments(self, parser):
        parser.add_argument(
            "app_labels",
            nargs="*",
            help="App labels whose tables will be truncated. If omitted, all tables are truncated.",
        )
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_true",
            help="Tells Django to NOT prompt the user for any confirmation.",
        )

    def handle(self, *args, **options):
        app_labels = options["app_labels"]
        noinput = options["noinput"]

        if app_labels:
            tables = []
            for label in app_labels:
                app_config = apps.get_app_config(label)
                for model in app_config.get_models():
                    tables.append(model._meta.db_table)
        else:
            tables = connection.introspection.table_names()

        tables = [t for t in tables if t != "django_migrations"]

        if not tables:
            self.stdout.write("No tables to truncate.")
            return

        if not noinput:
            self.stdout.write("The following tables will be truncated:")
            for t in tables:
                self.stdout.write(f"  {t}")
            confirm = input("Are you sure you want to truncate ALL DATA? [y/N] ")
            if confirm.lower() != "y":
                self.stdout.write("Aborted.")
                return

        vendor = connection.vendor
        with connection.cursor() as cursor:
            for table in tables:
                if vendor == "postgresql":
                    cursor.execute(
                        f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE;'
                    )
                elif vendor == "mysql":
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                    cursor.execute(f"TRUNCATE TABLE `{table}`;")
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                elif vendor == "sqlite":
                    cursor.execute(f'DELETE FROM "{table}";')
                    cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table}";')
                else:
                    cursor.execute(f'DELETE FROM "{table}";')
        self.stdout.write(self.style.SUCCESS("All data truncated successfully."))
