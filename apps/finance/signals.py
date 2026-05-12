from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Transaction, Budget
from apps.notifications.models import Notification


@receiver(post_save, sender=Transaction)
def check_budget_alert(sender, instance, created, **kwargs):
    if instance.is_expense and instance.category:
        from django.utils import timezone
        today = timezone.now().date()
        budgets = Budget.objects.filter(
            category=instance.category,
            period_start__lte=today,
            period_end__gte=today,
        )
        for budget in budgets:
            if budget.usage_percentage >= budget.alert_threshold:
                if instance.created_by:
                    Notification.objects.get_or_create(
                        user=instance.created_by,
                        title=f"Alerte budget: {budget.name}",
                        defaults={
                            'message': f"Votre budget '{budget.name}' est utilisé à {budget.usage_percentage}% ({budget.spent} / {budget.amount} FCFA).",
                            'notification_type': 'warning',
                            'action_url': '/finance/budgets/',
                        }
                    )
