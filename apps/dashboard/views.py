from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.finance.models import Transaction, Invoice, Budget, Category, CaisseMovement
from apps.documents.models import Document
from apps.audit.models import AuditLog
from apps.notifications.models import Notification


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (first_day - timedelta(days=1)).replace(day=1)
        last_month_end = first_day - timedelta(seconds=1)

        qs = Transaction.objects.filter(status='completed')

        # Current month stats
        month_qs = qs.filter(date__gte=first_day.date())
        revenues = month_qs.filter(
            transaction_type__in=['income', 'salary']
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        expenses = month_qs.filter(
            transaction_type__in=['expense', 'invoice']
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        profit = revenues - expenses

        # Last month for comparison
        lm_qs = qs.filter(date__range=[last_month_start.date(), last_month_end.date()])
        lm_revenues = lm_qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        lm_expenses = lm_qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or Decimal('0')

        def percent_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round(((current - previous) / previous) * 100, 1)

        # Chart data — last 6 months
        chart_labels = []
        chart_revenues = []
        chart_expenses = []
        months_fr = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun',
                     'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        for i in range(5, -1, -1):
            d = (now - timedelta(days=i * 30)).replace(day=1)
            label = f"{months_fr[d.month - 1]} {d.year}"
            month_end = (d + timedelta(days=32)).replace(day=1)
            m_qs = qs.filter(date__gte=d.date(), date__lt=month_end.date())
            rev = float(m_qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0)
            exp = float(m_qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0)
            chart_labels.append(label)
            chart_revenues.append(rev)
            chart_expenses.append(exp)

        # Expenses by category (pie)
        cat_data = month_qs.filter(
            transaction_type__in=['expense', 'invoice']
        ).values('category__name', 'category__color').annotate(
            total=Sum('amount')
        ).order_by('-total')[:6]

        # Recent transactions
        recent_transactions = Transaction.objects.select_related(
            'category', 'created_by'
        ).order_by('-created_at')[:8]

        # Recent documents
        recent_docs = Document.objects.filter(status='active').order_by('-created_at')[:5]

        # Pending invoices
        pending_invoices = Invoice.objects.filter(
            status__in=['pending', 'overdue']
        ).order_by('due_date')[:5]

        # Recent activity (audit)
        recent_activity = AuditLog.objects.select_related('user').order_by('-timestamp')[:10]

        # Budgets
        budgets = Budget.objects.filter(
            period_start__lte=now.date(),
            period_end__gte=now.date()
        ).select_related('category')[:4]

        ctx.update({
            'revenues': revenues,
            'expenses': expenses,
            'profit': profit,
            'caisse_balance': CaisseMovement.get_balance(),
            'transaction_count': month_qs.count(),
            'revenue_change': percent_change(revenues, lm_revenues),
            'expense_change': percent_change(expenses, lm_expenses),
            'chart_labels': chart_labels,
            'chart_revenues': chart_revenues,
            'chart_expenses': chart_expenses,
            'cat_data': list(cat_data),
            'recent_transactions': recent_transactions,
            'recent_docs': recent_docs,
            'pending_invoices': pending_invoices,
            'recent_activity': recent_activity,
            'budgets': budgets,
            'now': now,
        })
        return ctx
