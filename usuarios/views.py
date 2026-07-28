from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import PerfilForm


def perfil(request):
    if request.method == "POST":
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("usuarios:perfil")
    else:
        form = PerfilForm(instance=request.user)

    return render(request, "usuarios/perfil.html", {"form": form})
