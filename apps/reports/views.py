from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, View
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import Report
from apps.finance.models import Transaction, Category, CaisseMovement
from apps.audit.utils import log_action
from apps.audit.models import AuditLog


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        return Report.objects.select_related('generated_by').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Sum

        now = timezone.now()
        first_day = now.replace(day=1).date()

        # Solde avant les transactions du mois (solde d'ouverture)
        c_before = CaisseMovement.objects.filter(
            movement_type='credit', created_at__date__lt=first_day
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        d_before = CaisseMovement.objects.filter(
            movement_type='debit', created_at__date__lt=first_day
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        ctx['caisse_opening'] = c_before - d_before

        # Mouvements du mois en cours
        ctx['caisse_credits_month'] = CaisseMovement.objects.filter(
            movement_type='credit', created_at__date__gte=first_day
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        ctx['caisse_debits_month'] = CaisseMovement.objects.filter(
            movement_type='debit', created_at__date__gte=first_day
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')

        # Solde actuel (après toutes les transactions)
        ctx['caisse_current'] = CaisseMovement.get_balance()
        ctx['current_month'] = now.strftime('%B %Y')
        return ctx


class ReportCreateView(LoginRequiredMixin, View):
    def post(self, request):
        report_type = request.POST.get('report_type')
        period_start = request.POST.get('period_start')
        period_end = request.POST.get('period_end')
        export_format = request.POST.get('export_format', 'pdf')

        report = Report.objects.create(
            title=f"Rapport {Report.ReportType(report_type).label}",
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            export_format=export_format,
            generated_by=request.user,
        )

        from apps.reports.tasks import generate_report_task
        try:
            generate_report_task.delay(str(report.pk))
            messages.success(request, "Rapport en cours de génération. Vous serez notifié.")
        except Exception:
            generate_report_task.apply(args=[str(report.pk)])
            messages.success(request, "Rapport généré avec succès.")
        from django.shortcuts import redirect
        return redirect('reports:list')


class ReportDownloadView(LoginRequiredMixin, View):
    CONTENT_TYPES = {
        'pdf': 'application/pdf',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'csv': 'text/csv',
    }

    def get(self, request, pk):
        from django.shortcuts import redirect
        report = get_object_or_404(Report, pk=pk)

        if report.status != 'completed':
            messages.error(request, "Le rapport n'est pas encore prêt. Veuillez patienter.")
            return redirect('reports:list')

        if not report.file:
            # File missing but status completed — regenerate synchronously
            from .utils import generate_report_file
            from django.core.files.base import ContentFile
            from django.utils import timezone as tz
            file_content, filename = generate_report_file(report)
            report.file.save(filename, ContentFile(file_content), save=False)
            report.completed_at = tz.now()
            report.save()

        content_type = self.CONTENT_TYPES.get(report.export_format, 'application/octet-stream')
        ext = report.export_format if report.export_format != 'excel' else 'xlsx'
        safe_title = report.title.replace(' ', '_').replace('/', '-')

        report.file.open('rb')
        response = HttpResponse(report.file.read(), content_type=content_type)
        report.file.close()
        response['Content-Disposition'] = f'attachment; filename="{safe_title}.{ext}"'

        log_action(
            user=request.user,
            action=AuditLog.ActionType.EXPORT,
            instance=report,
            description=f"{request.user} a téléchargé le rapport: {report.title}",
            request=request,
        )
        return response


class FinancialSummaryAPIView(LoginRequiredMixin, View):
    def get(self, request):
        now = timezone.now()
        period = request.GET.get('period', 'month')

        if period == 'month':
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == 'year':
            start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start = now - timedelta(days=30)

        qs = Transaction.objects.filter(date__gte=start.date(), status='completed')
        revenues = float(qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0)
        expenses = float(qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0)

        return JsonResponse({
            'revenues': revenues,
            'expenses': expenses,
            'profit': revenues - expenses,
            'count': qs.count(),
        })
