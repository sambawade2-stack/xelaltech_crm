import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class AuditLog(models.Model):
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Création'
        UPDATE = 'update', 'Modification'
        DELETE = 'delete', 'Suppression'
        VIEW = 'view', 'Consultation'
        EXPORT = 'export', 'Export'
        LOGIN = 'login', 'Connexion'
        LOGOUT = 'logout', 'Déconnexion'
        FAILED_LOGIN = 'failed_login', 'Échec connexion'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=500, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        user_str = str(self.user) if self.user else 'Anonyme'
        return f"{user_str} — {self.get_action_display()} — {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    @property
    def human_description(self):
        if self.description:
            return self.description
        user_str = str(self.user) if self.user else 'Anonyme'
        return f"{user_str} a effectué une action '{self.get_action_display()}' sur {self.object_repr}"
