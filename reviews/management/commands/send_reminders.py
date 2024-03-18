from django.core.management.base import BaseCommand

from reviews.utils import remind_reviewers


class Command(BaseCommand):
    help = "Sends reminders to reviewers for short route reviews that needs to be decided in the next 2 days"

    def handle(self, *args, **options):
        remind_reviewers()
