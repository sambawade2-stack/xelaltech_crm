import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('apps.reports')


@shared_task(bind=True, max_retries=3)
def generate_report_task(self, report_id):
    try:
        from .models import Report
        from .utils import generate_report_file
        from apps.finance.models import Transaction, Category
        from django.db.models import Sum
        from django.core.files.base import ContentFile

        report = Report.objects.get(pk=report_id)
        report.status = 'pending'
        report.save()

        from apps.finance.models import CaisseMovement
        qs = Transaction.objects.filter(
            date__range=[report.period_start, report.period_end],
            status='completed'
        )

        revenues = float(qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0)
        expenses = float(qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0)

        # Breakdown by category
        by_category = {}
        for cat in Category.objects.filter(is_active=True):
            total = qs.filter(category=cat).aggregate(t=Sum('amount'))['t']
            if total:
                by_category[cat.name] = float(total)

        # ── Caisse : solde avant / pendant / après la période ──────────
        c_before = float(CaisseMovement.objects.filter(
            movement_type='credit', created_at__date__lt=report.period_start
        ).aggregate(t=Sum('amount'))['t'] or 0)
        d_before = float(CaisseMovement.objects.filter(
            movement_type='debit', created_at__date__lt=report.period_start
        ).aggregate(t=Sum('amount'))['t'] or 0)
        caisse_opening = c_before - d_before

        c_period = float(CaisseMovement.objects.filter(
            movement_type='credit',
            created_at__date__range=[report.period_start, report.period_end]
        ).aggregate(t=Sum('amount'))['t'] or 0)
        d_period = float(CaisseMovement.objects.filter(
            movement_type='debit',
            created_at__date__range=[report.period_start, report.period_end]
        ).aggregate(t=Sum('amount'))['t'] or 0)

        caisse_closing = caisse_opening + c_period - d_period
        caisse_current  = float(CaisseMovement.get_balance())

        report.data = {
            'revenues': revenues,
            'expenses': expenses,
            'profit': revenues - expenses,
            'transaction_count': qs.count(),
            'by_category': by_category,
            'caisse_opening':  caisse_opening,
            'caisse_credits':  c_period,
            'caisse_debits':   d_period,
            'caisse_closing':  caisse_closing,
            'caisse_current':  caisse_current,
        }

        # Generate and save the actual file
        file_content, filename = generate_report_file(report)
        report.file.save(filename, ContentFile(file_content), save=False)

        report.status = 'completed'
        report.completed_at = timezone.now()
        report.save()

        from apps.notifications.models import Notification
        Notification.objects.create(
            user=report.generated_by,
            title="Rapport généré",
            message=f"Votre rapport '{report.title}' est prêt.",
            notification_type='success',
            action_url=f'/reports/{report.pk}/download/',
            action_label='Télécharger',
        )
        logger.info(f"Report {report_id} generated successfully")

    except Exception as exc:
        logger.error(f"Report generation failed: {exc}")
        try:
            from .models import Report
            Report.objects.filter(pk=report_id).update(status='failed')
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=60)


@shared_task
def check_overdue_invoices():
    from apps.finance.models import Invoice
    from apps.notifications.models import Notification
    from django.utils import timezone

    today = timezone.now().date()
    overdue = Invoice.objects.filter(status='pending', due_date__lt=today)
    for invoice in overdue:
        invoice.status = 'overdue'
        invoice.save()
        if invoice.created_by:
            Notification.objects.create(
                user=invoice.created_by,
                title=f"Facture en retard: {invoice.invoice_number}",
                message=f"La facture {invoice.invoice_number} de {invoice.total} FCFA était due le {invoice.due_date.strftime('%d/%m/%Y')}.",
                notification_type='error',
                action_url=f'/finance/invoices/{invoice.pk}/',
            )
    logger.info(f"{overdue.count()} factures marquées comme en retard")


@shared_task
def send_budget_alerts():
    from apps.finance.models import Budget
    from apps.notifications.models import Notification
    from django.utils import timezone

    today = timezone.now().date()
    budgets = Budget.objects.filter(period_start__lte=today, period_end__gte=today)
    for budget in budgets:
        if budget.usage_percentage >= budget.alert_threshold and budget.created_by:
            Notification.objects.get_or_create(
                user=budget.created_by,
                title=f"Budget dépassé: {budget.name}",
                defaults={
                    'message': f"Budget '{budget.name}' à {budget.usage_percentage}%.",
                    'notification_type': 'warning',
                }
            )
