import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger('apps.audit')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request._audit_ip = get_client_ip(request)
        request._audit_user_agent = request.META.get('HTTP_USER_AGENT', '')
        response = self.get_response(request)
        return response


@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=AuditLog.ActionType.LOGIN,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        description=f"{user} s'est connecté",
    )


@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    from .models import AuditLog
    if user:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.ActionType.LOGOUT,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            description=f"{user} s'est déconnecté",
        )


@receiver(user_login_failed)
def log_login_failed(sender, credentials, request, **kwargs):
    from .models import AuditLog
    AuditLog.objects.create(
        action=AuditLog.ActionType.FAILED_LOGIN,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        description=f"Tentative de connexion échouée pour: {credentials.get('email', credentials.get('username', 'inconnu'))}",
    )
