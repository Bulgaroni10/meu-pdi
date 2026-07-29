from django.db import migrations


def reset_personal_content(apps, schema_editor):
    Usuario = apps.get_model("usuarios", "Usuario")
    usuario = Usuario.objects.order_by("pk").first()
    if usuario is None:
        return

    ordered_models = (
        ("revisoes", "AcaoRevisao"),
        ("revisoes", "RevisaoPeriodica"),
        ("competencias", "EvidenciaCompetencia"),
        ("competencias", "AvaliacaoCompetencia"),
        ("competencias", "Competencia"),
        ("certificacoes", "Certificacao"),
        ("anotacoes", "Anotacao"),
        ("biblioteca", "MaterialPDF"),
        ("projetos", "Evidencia"),
        ("projetos", "ProjetoTecnologia"),
        ("projetos", "TarefaProjeto"),
        ("projetos", "MarcoProjeto"),
        ("projetos", "Projeto"),
        ("projetos", "Tecnologia"),
        ("roadmap", "Roadmap"),
        ("roadmap", "FonteRoadmap"),
        ("estudos", "SessaoEstudo"),
        ("estudos", "Aula"),
        ("estudos", "Disciplina"),
        ("estudos", "Periodo"),
        ("estudos", "Curso"),
        ("estudos", "Trilha"),
        ("objetivos", "Objetivo"),
        ("objetivos", "Tag"),
    )
    for app_label, model_name in ordered_models:
        apps.get_model(app_label, model_name).objects.filter(usuario=usuario).delete()

    for field in (
        "cargo_atual",
        "cargo_desejado",
        "resumo_profissional",
        "objetivo_principal",
        "localizacao",
        "github_url",
        "linkedin_url",
    ):
        setattr(usuario, field, "")
    usuario.save()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0002_perfil_profissional"),
        ("objetivos", "0001_initial"),
        ("roadmap", "0001_initial"),
        ("estudos", "0002_sessaoestudo"),
        ("biblioteca", "0001_initial"),
        ("anotacoes", "0001_initial"),
        ("projetos", "0002_evidencia_imagem"),
        ("competencias", "0001_initial"),
        ("revisoes", "0001_initial"),
        ("certificacoes", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(reset_personal_content, migrations.RunPython.noop),
    ]
