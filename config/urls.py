from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.users.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('finance/', include('apps.finance.urls')),
    path('reports/', include('apps.reports.urls')),
    path('documents/', include('apps.documents.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('audit/', include('apps.audit.urls')),
    path('api/v1/', include('apps.api.urls')),
    path('accounts/', include('allauth.urls')),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'FinTrack CRM Admin'
admin.site.site_title = 'FinTrack CRM'
admin.site.index_title = 'Administration'
