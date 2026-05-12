from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from apps.notifications.models import Notification

@receiver(post_save, sender=User)
def create_welcome_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance,
            title="Bienvenue sur FinTrack CRM",
            message=f"Bonjour {instance.get_full_name() or instance.username}, votre compte a été créé avec succès.",
            notification_type='info',
        )
