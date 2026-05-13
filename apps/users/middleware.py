from django.http import HttpResponse
from django_ratelimit.core import is_ratelimited

# Règles par préfixe de chemin : (préfixe, rate, méthodes)
_ROUTE_RULES = [
    ('/auth/login',           '10/m',  None),
    ('/auth/register',        '5/m',   None),
    ('/auth/password-reset',  '5/m',   None),
    ('/accounts/',            '10/m',  None),
    ('/api/',                 '60/m',  None),
]
_GLOBAL_RATE = '200/m'


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rate = self._get_rate(request.path)
        limited = is_ratelimited(
            request,
            group='crm:' + request.path.split('/')[1],
            key='ip',
            rate=rate,
            increment=True,
        )
        if limited:
            return HttpResponse(
                '429 — Trop de requêtes. Veuillez patienter quelques instants.',
                status=429,
                content_type='text/plain; charset=utf-8',
            )
        return self.get_response(request)

    def _get_rate(self, path):
        for prefix, rate, _ in _ROUTE_RULES:
            if path.startswith(prefix):
                return rate
        return _GLOBAL_RATE
