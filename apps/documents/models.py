import uuid
import os
from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


def document_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"documents/{instance.document_type}/{instance.uploaded_by.id}/{uuid.uuid4()}.{ext}"


class Document(models.Model):
    class DocumentType(models.TextChoices):
        CONTRACT = 'contract', 'Contrat'
        RECEIPT = 'receipt', 'Reçu'
        INVOICE = 'invoice', 'Facture'
        REPORT = 'report', 'Rapport'
        ID_DOCUMENT = 'id', 'Pièce d\'identité'
        OTHER = 'other', 'Autre'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Actif'
        ARCHIVED = 'archived', 'Archivé'
        DELETED = 'deleted', 'Supprimé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_path)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    file_size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    related_transaction = models.ForeignKey(
        'finance.Transaction', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='documents'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='documents_uploaded'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1].lower().strip('.')
        super().save(*args, **kwargs)

    @property
    def file_size_display(self):
        size = self.file_size
        for unit in ['o', 'Ko', 'Mo', 'Go']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} To"

    @property
    def is_image(self):
        return self.file_type in ['jpg', 'jpeg', 'png', 'gif', 'webp']

    @property
    def is_pdf(self):
        return self.file_type == 'pdf'
