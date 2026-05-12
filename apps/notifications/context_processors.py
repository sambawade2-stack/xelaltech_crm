def notifications(request):
    if request.user.is_authenticated:
        unread_count = request.user.notifications.filter(is_read=False).count()
        recent = request.user.notifications.filter(is_read=False).order_by('-created_at')[:5]
        try:
            from apps.finance.models import BudgetRequest
            pending_br = BudgetRequest.objects.filter(status='pending').count()
        except Exception:
            pending_br = 0
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent,
            'pending_budget_requests_count': pending_br,
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': [],
        'pending_budget_requests_count': 0,
    }
