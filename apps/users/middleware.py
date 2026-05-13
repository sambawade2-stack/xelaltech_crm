import logging
from django.http import HttpResponse
from django_ratelimit.core import is_ratelimited

logger = logging.getLogger(__name__)

_ROUTE_RULES = [
    ('/auth/login',          '10/m'),
    ('/auth/register',       '5/m'),
    ('/auth/password-reset', '5/m'),
    ('/accounts/',           '10/m'),
    ('/api/',                '60/m'),
]
_GLOBAL_RATE = '200/m'


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
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
        except Exception:
            # Cache indisponible (table manquante, Redis down…) — on laisse passer
            logger.warning('RateLimitMiddleware: cache indisponible, rate limit désactivé temporairement.')

        return self.get_response(request)

    def _get_rate(self, path):
        for prefix, rate in _ROUTE_RULES:
            if path.startswith(prefix):
                return rate
        return _GLOBAL_RATE
