def company_settings(request):
    try:
        from .models import CompanySettings
        return {'company': CompanySettings.get()}
    except Exception:
        return {'company': None}
