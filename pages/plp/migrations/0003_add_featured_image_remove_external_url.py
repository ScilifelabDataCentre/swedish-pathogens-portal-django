from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plp", "0002_seed_initial_projects"),
    ]

    operations = [
        migrations.AddField(
            model_name="plpproject",
            name="featured_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="plp/projects/",
                help_text="Featured image for the project (optional)",
            ),
        ),
        migrations.RemoveField(
            model_name="plpproject",
            name="external_url",
        ),
    ]

