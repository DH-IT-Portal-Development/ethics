# Generated by Django 3.2.14 on 2022-08-24 14:28

from django.db import migrations

def choose_review_type(apps, schema_editor):
    Review = apps.get_model("reviews", "Review")
    for review in Review.objects.all():
        if review.stage == review.SUPERVISOR:
            review.review_type = "supervisor"
        else:
            review.review_type = "committee"


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0013_review_review_type'),
    ]

    operations = [
        migrations.RunPython(choose_review_type),
    ]
