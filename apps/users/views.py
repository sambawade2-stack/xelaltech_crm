from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

from .models import User, CompanySettings
from .forms import UserProfileForm, UserRegistrationForm, CompanySettingsForm, UserCreateForm, UserEditForm
from .mixins import AdminRequiredMixin


class LoginView(TemplateView):
    template_name = 'auth/login.html'


class RegisterView(TemplateView):
    template_name = 'auth/register.html'


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['form'] = UserProfileForm(instance=self.request.user)
        ctx['password_form'] = PasswordChangeForm(user=self.request.user)
        return ctx

    def post(self, request):
        action = request.POST.get('action')

        if action == 'change_password':
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Mot de passe modifié avec succès.")
                return redirect('users:profile')
            ctx = self.get_context_data()
            ctx['password_form'] = password_form
            ctx['open_password'] = True
            return render(request, self.template_name, ctx)

        if action == 'update_profile':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profil mis à jour avec succès.")
                return redirect('users:profile')
            ctx = self.get_context_data()
            ctx['form'] = form
            return render(request, self.template_name, ctx)

        return redirect('users:profile')


class ThemeToggleView(LoginRequiredMixin, View):
    def post(self, request):
        theme = request.POST.get('theme', 'light')
        if theme in ('light', 'dark'):
            request.user.theme = theme
            request.user.save(update_fields=['theme'])
        next_url = request.POST.get('next', '/')
        return redirect(next_url)


class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['company'] = CompanySettings.get()
        if self.request.user.is_admin:
            ctx['company_form'] = CompanySettingsForm(instance=CompanySettings.get())
        return ctx

    def post(self, request):
        if not request.user.is_admin:
            messages.error(request, "Seul un administrateur peut modifier les paramètres de l'entreprise.")
            return redirect('users:settings')
        instance = CompanySettings.get()
        form = CompanySettingsForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Paramètres de l'entreprise mis à jour.")
        else:
            messages.error(request, "Erreur dans le formulaire.")
        return redirect('users:settings')


class UserListView(AdminRequiredMixin, TemplateView):
    template_name = 'users/list.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['users'] = User.objects.all().order_by('role', '-created_at')
        ctx['create_form'] = UserCreateForm()
        return ctx

    def post(self, request):
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Utilisateur {user.get_full_name() or user.username} créé avec le rôle {user.get_role_display()}.")
            return redirect('users:list')
        ctx = self.get_context_data()
        ctx['create_form'] = form
        ctx['show_create_modal'] = True
        return render(request, self.template_name, ctx)


class UserToggleActiveView(AdminRequiredMixin, TemplateView):
    template_name = 'users/list.html'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
            return redirect('users:list')
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"Compte de {user.get_full_name() or user.username} {status}.")
        return redirect('users:list')


class UserEditView(AdminRequiredMixin, TemplateView):
    template_name = 'users/list.html'

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Utilisateur {user.get_full_name() or user.username} mis à jour.")
        else:
            messages.error(request, "Erreur lors de la modification.")
        return redirect('users:list')
