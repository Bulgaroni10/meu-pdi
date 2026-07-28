import projetos.models
import projetos.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("projetos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="evidencia",
            name="imagem",
            field=models.FileField(
                blank=True,
                help_text="PNG, JPG ou WebP, com no máximo 8 MB.",
                upload_to=projetos.models.caminho_imagem_evidencia,
                validators=[projetos.validators.validar_imagem_evidencia],
                verbose_name="imagem da captura",
            ),
        ),
    ]
