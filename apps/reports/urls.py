from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='list'),
    path('generate/', views.ReportCreateView.as_view(), name='create'),
    path('<uuid:pk>/download/', views.ReportDownloadView.as_view(), name='download'),
    path('api/summary/', views.FinancialSummaryAPIView.as_view(), name='api_summary'),
]
