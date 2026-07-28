from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="usuario",
            name="github_url",
            field=models.URLField(blank=True, verbose_name="GitHub"),
        ),
        migrations.AddField(
            model_name="usuario",
            name="linkedin_url",
            field=models.URLField(blank=True, verbose_name="LinkedIn"),
        ),
        migrations.AddField(
            model_name="usuario",
            name="localizacao",
            field=models.CharField(blank=True, max_length=120, verbose_name="localização"),
        ),
        migrations.AddField(
            model_name="usuario",
            name="resumo_profissional",
            field=models.TextField(
                blank=True,
                help_text="Uma apresentação curta sobre sua experiência, interesses e direção profissional.",
                verbose_name="sobre mim",
            ),
        ),
    ]
