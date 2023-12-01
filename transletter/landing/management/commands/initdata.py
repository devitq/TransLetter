from django.core.management import call_command
from django.core.management.base import BaseCommand

__all__ = ""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--interactive",
            action="store_true",
            help=(
                "Input superuser data in console"
                "instead of getting it from env"
            ),
        )
        parser.add_argument(
            "--skip-applying-migrations",
            action="store_true",
            help=("Add this to stop loading migrations"),
        )
        parser.add_argument(
            "--skip-loading-fixtures",
            action="store_true",
            help=("Add this to stop loading fixtures"),
        )
        parser.add_argument(
            "--skip-creating-superuser",
            action="store_true",
            help=("Add this to stop creating superuser"),
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Applying migrations..."))
        if not options["skip_applying_migrations"]:
            call_command("migrate")
            self.stdout.write(self.style.SUCCESS("Loaded"))
        else:
            self.stdout.write(self.style.WARNING("Skipped"))

        self.stdout.write(self.style.SUCCESS("Loading fixtures..."))
        if not options["skip_loading_fixtures"]:
            call_command("loaddata", "fixtures/data.json")
            self.stdout.write(self.style.SUCCESS("Loaded"))
        else:
            self.stdout.write(self.style.WARNING("Skipped"))

        self.stdout.write(self.style.SUCCESS("Creating superuser..."))
        if not options["skip_creating_superuser"]:
            if options["interactive"]:
                call_command("createsuperuser")
            else:
                call_command("createsuperuser", interactive=False)
        else:
            self.stdout.write(self.style.WARNING("Skipped"))

        self.stdout.write(self.style.SUCCESS("Ended successfully"))
