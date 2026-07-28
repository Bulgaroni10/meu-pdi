from django.db import transaction

from .models import MarcoProjeto, Projeto, TarefaProjeto


@transaction.atomic
def recalcular_progresso(projeto: Projeto) -> int:
    tarefas = projeto.tarefas.all()
    marcos = projeto.marcos.all()
    componentes = []
    if tarefas.exists():
        componentes.append(
            tarefas.filter(status=TarefaProjeto.Status.CONCLUIDA).count()
            * 100
            / tarefas.count()
        )
    if marcos.exists():
        componentes.append(
            marcos.filter(status=MarcoProjeto.Status.CONCLUIDO).count()
            * 100
            / marcos.count()
        )
    if not componentes:
        return projeto.progresso

    projeto.progresso = round(sum(componentes) / len(componentes))
    if projeto.progresso == 100:
        projeto.status = Projeto.Status.CONCLUIDO
    elif projeto.status in (Projeto.Status.IDEIA, Projeto.Status.PLANEJADO):
        projeto.status = Projeto.Status.EM_ANDAMENTO
    projeto.save(update_fields=("progresso", "status", "data_conclusao", "updated_at"))
    return projeto.progresso
