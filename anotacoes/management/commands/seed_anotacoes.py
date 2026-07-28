from django.core.management.base import BaseCommand

from anotacoes.models import Anotacao, VersaoAnotacao
from anotacoes.services import sanitizar_html
from estudos.models import Aula
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Cria uma anotação demonstrativa editável."

    def handle(self, *args, **options):
        usuario = Usuario.objects.get(pk=1)
        aula = Aula.objects.filter(usuario=usuario).first()
        if not aula:
            self.stdout.write(self.style.WARNING("Cadastre uma aula antes da anotação."))
            return
        html = sanitizar_html(
            "<h2>Modelo de responsabilidade compartilhada</h2>"
            "<p>Na nuvem, provedor e cliente dividem responsabilidades de segurança.</p>"
            "<ul><li>O provedor protege a infraestrutura física.</li>"
            "<li>O cliente protege identidades, dados e configurações.</li></ul>"
        )
        nota, created = Anotacao.objects.get_or_create(
            usuario=usuario,
            aula=aula,
            titulo="Responsabilidade compartilhada no Azure",
            defaults={
                "tipo": Anotacao.Tipo.RESUMO,
                "conteudo_html": html,
                "conteudo_texto": (
                    "Modelo de responsabilidade compartilhada. Na nuvem, provedor "
                    "e cliente dividem responsabilidades de segurança."
                ),
                "pagina_pdf": 1,
                "tags": "azure, segurança, fundamentos",
            },
        )
        if created:
            VersaoAnotacao.objects.create(
                usuario=usuario,
                anotacao=nota,
                numero=1,
                titulo=nota.titulo,
                conteudo_html=nota.conteudo_html,
                conteudo_texto=nota.conteudo_texto,
            )
        self.stdout.write(self.style.SUCCESS("Anotação demonstrativa pronta."))
