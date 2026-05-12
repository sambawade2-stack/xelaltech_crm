from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class RoleRequiredMixin(LoginRequiredMixin):
    """Override allowed_roles = ('admin',) in the view class."""
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if self.allowed_roles and request.user.role not in self.allowed_roles:
            messages.error(request, "Vous n'avez pas les droits nécessaires pour accéder à cette page.")
            return redirect('dashboard:index')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ('admin',)


class FinanceRequiredMixin(RoleRequiredMixin):
    """Admin + Comptable."""
    allowed_roles = ('admin', 'comptable')
