from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings

import os


def list_fixtures_in_dir(rel_path):
    files = os.listdir(rel_path)

    def is_fixture(fn):
        return fn.lower()[-5:] == ".json"

    return [os.path.join(rel_path, fn) for fn in files if is_fixture(fn)]


fixture_dirs = {
    "proposals": list_fixtures_in_dir("proposals/fixtures/"),
    "studies": list_fixtures_in_dir("studies/fixtures/"),
    "tasks": list_fixtures_in_dir("tasks/fixtures/"),
    "observations": list_fixtures_in_dir("observations/fixtures/"),
    "main": list_fixtures_in_dir("main/fixtures/"),
}


class Command(BaseCommand):
    help = "Loads fixtures for development in the correct order."

    def add_arguments(self, parser):
        parser.add_argument("--force", action="store_true")

    def handle(self, *args, **kwargs):
        if not settings.DEBUG and not kwargs["force"]:
            raise CommandError(
                "Refusing to execute command unless DEBUG = True in settings.py"
            )

        print("Loading fixtures...")

        for app, locations in fixture_dirs.items():
            print(f"for {app}")
            for loc in locations:
                call_command("loaddata", loc)

        print("Done!")
