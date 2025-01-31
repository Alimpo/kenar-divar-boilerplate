# Generated by Django 4.1 on 2024-06-30 07:54

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="StateSession",
            fields=[
                (
                    "state",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "session_type",
                    models.CharField(
                        choices=[("CHAT", "Chat"), ("POST", "Post")], max_length=10
                    ),
                ),
                ("callback_url", models.URLField()),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name="TokenSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "access_token",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "refresh_token",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("expires_in", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
