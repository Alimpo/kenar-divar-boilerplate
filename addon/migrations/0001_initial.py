# Generated by Django 4.1 on 2024-06-30 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("oauth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PostSession",
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
                ("token", models.CharField(max_length=50)),
                (
                    "oauth_state_session",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="oauth.statesession",
                    ),
                ),
                (
                    "oauth_token_session",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="oauth.tokensession",
                    ),
                ),
            ],
        ),
    ]
