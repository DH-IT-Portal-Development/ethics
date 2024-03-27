# Generated by Django 3.2.20 on 2023-11-16 13:01

from django.db import migrations, models


def update_is_committee_review(apps, schema_editor):
    Review = apps.get_model("reviews", "Review")

    for review in Review.objects.all():
        # Hardcoded these to account for possible future changes to stages
        SUPERVISOR_STAGE = 0
        CLOSED_STAGE = 4
        if review.stage == SUPERVISOR_STAGE:
            review.is_committee_review = False
            if review.go:
                review.stage = CLOSED_STAGE
            review.save()


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0012_auto_20211213_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="is_committee_review",
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(update_is_committee_review),
    ]