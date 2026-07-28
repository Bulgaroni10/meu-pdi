from django.shortcuts import render
from django.utils import timezone

from certificacoes.models import Certificacao
from competencias.selectors import competencias_do_usuario
from objetivos.models import Objetivo
from projetos.models import Projeto
from .selectors import visao_indicadores


def painel(request):
    return render(
        request,
        "indicadores/painel.html",
        visao_indicadores(request.user),
    )


def relatorio(request):
    contexto = visao_indicadores(request.user)
    contexto.update(
        {
            "gerado_em": timezone.localtime(),
            "objetivo_principal": Objetivo.objects.filter(
                usuario=request.user, arquivado_em__isnull=True
            ).first(),
            "projetos_destaque": Projeto.objects.filter(
                usuario=request.user, arquivado_em__isnull=True
            )[:3],
            "competencias_destaque": competencias_do_usuario(request.user).filter(
                arquivado_em__isnull=True
            )[:5],
            "certificacoes_destaque": Certificacao.objects.filter(
                usuario=request.user, arquivado_em__isnull=True
            )[:3],
        }
    )
    return render(request, "indicadores/relatorio.html", contexto)
