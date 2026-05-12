from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Q
from .models import AuditLog


class AuditLogListView(LoginRequiredMixin, ListView):
    model = AuditLog
    template_name = 'audit/list.html'
    context_object_name = 'logs'
    paginate_by = 30

    def get_queryset(self):
        qs = AuditLog.objects.select_related('user').order_by('-timestamp')
        user = self.request.user
        if user.role not in ['admin', 'auditor']:
            qs = qs.filter(user=user)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(description__icontains=q) | Q(object_repr__icontains=q))
        action = self.request.GET.get('action')
        if action:
            qs = qs.filter(action=action)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['action_choices'] = AuditLog.ActionType.choices
        return ctx
