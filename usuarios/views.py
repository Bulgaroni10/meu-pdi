from django.contrib import messages
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, PerfilForm


class LoginPessoalView(LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get("lembrar"):
            self.request.session.set_expiry(None)
        else:
            self.request.session.set_expiry(0)
        return response


class AlterarSenhaView(PasswordChangeView):
    template_name = "usuarios/alterar_senha.html"
    success_url = reverse_lazy("usuarios:perfil")

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada com sucesso.")
        return super().form_valid(form)


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
