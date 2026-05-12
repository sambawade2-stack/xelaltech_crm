import uuid
from django.db import models
from django.conf import settings


class Report(models.Model):
    class ReportType(models.TextChoices):
        MONTHLY = 'monthly', 'Rapport mensuel'
        ANNUAL = 'annual', 'Rapport annuel'
        CASHFLOW = 'cashflow', 'Cash Flow'
        EXPENSE_BY_CATEGORY = 'expense_category', 'Dépenses par catégorie'
        CUSTOM = 'custom', 'Personnalisé'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En cours'
        COMPLETED = 'completed', 'Terminé'
        FAILED = 'failed', 'Échoué'

    class ExportFormat(models.TextChoices):
        PDF = 'pdf', 'PDF'
        EXCEL = 'excel', 'Excel'
        CSV = 'csv', 'CSV'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=ReportType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    period_start = models.DateField()
    period_end = models.DateField()
    export_format = models.CharField(max_length=10, choices=ExportFormat.choices, default=ExportFormat.PDF)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    data = models.JSONField(default=dict, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='reports_generated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Rapport'
        verbose_name_plural = 'Rapports'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"
