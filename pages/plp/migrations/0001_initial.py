from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PlpProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Project title (e.g., 'Multi-disease serology')", max_length=255, unique=True)),
                ("slug", models.SlugField(blank=True, help_text="URL-friendly identifier (auto-generated from title if blank)", max_length=255, unique=True)),
                ("category", models.CharField(choices=[("plp1", "PLP1"), ("plp2", "PLP2"), ("tdp", "TDP"), ("test", "PLP-Test"), ("pmt", "PM TDP"), ("other", "Other")], default="other", help_text="Project category (e.g., PLP1, PLP2, TDP)", max_length=20)),
                ("summary", models.TextField(help_text="Short blurb shown on cards and listings (plain text)")),
                ("content", models.TextField(help_text="Full markdown content for the project detail page")),
                ("external_url", models.URLField(blank=True, help_text="Optional external link for the project")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now, help_text="Creation timestamp (defaults to now)")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("is_active", models.BooleanField(default=True, help_text="Toggle visibility without deleting the record")),
            ],
            options={
                "verbose_name": "PLP Project",
                "verbose_name_plural": "PLP Projects",
                "ordering": ["-created_at"],
            },
        ),
    ]



