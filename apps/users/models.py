import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN     = 'admin',     'Administrateur'
        COMPTABLE = 'comptable', 'Comptable'
        MEMBRE    = 'membre',    'Membre'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBRE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    theme = models.CharField(max_length=10, default='light', choices=[('light', 'Clair'), ('dark', 'Sombre')])
    language = models.CharField(max_length=10, default='fr')
    timezone = models.CharField(max_length=50, default='Africa/Dakar')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    FINANCE_ROLES = ('admin', 'comptable')

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_comptable(self):
        return self.role == 'comptable'

    @property
    def is_membre(self):
        return self.role == 'membre'

    @property
    def can_access_finance(self):
        return self.role in self.FINANCE_ROLES

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        initials = (self.first_name[:1] + self.last_name[:1]).upper() or self.username[:2].upper()
        return f"https://ui-avatars.com/api/?name={initials}&background=2563EB&color=fff&size=128"


class CompanySettings(models.Model):
    name = models.CharField(max_length=200, default='Xelaltech221 CRM')
    tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='company/', null=True, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    website = models.URLField(blank=True)
    currency = models.CharField(max_length=10, default='FCFA')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètres entreprise'

    def __str__(self):
        return self.name

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'name': 'Xelaltech221 CRM'})
        return obj


class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_activity']
