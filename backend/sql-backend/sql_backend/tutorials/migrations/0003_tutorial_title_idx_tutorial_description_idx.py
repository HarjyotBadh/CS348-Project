# Generated by Django 5.0.3 on 2024-04-28 19:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tutorials", "0002_tutorial_users"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name="tutorial",
            index=models.Index(fields=["title"], name="title_idx"),
        ),
        migrations.AddIndex(
            model_name="tutorial",
            index=models.Index(fields=["description"], name="description_idx"),
        ),
    ]
