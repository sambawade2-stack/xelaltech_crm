from django.contrib.contenttypes.models import ContentType
from .models import AuditLog


def log_action(user, action, instance=None, old_values=None, new_values=None,
               description='', request=None):
    ip = None
    user_agent = ''
    if request:
        ip = getattr(request, '_audit_ip', None)
        user_agent = getattr(request, '_audit_user_agent', '')

    content_type = None
    object_id = None
    object_repr = ''
    if instance:
        content_type = ContentType.objects.get_for_model(instance)
        object_id = str(instance.pk)
        object_repr = str(instance)

    changes = {}
    if old_values and new_values:
        for key in set(list(old_values.keys()) + list(new_values.keys())):
            old_val = old_values.get(key)
            new_val = new_values.get(key)
            if old_val != new_val:
                changes[key] = {'old': old_val, 'new': new_val}

    AuditLog.objects.create(
        user=user,
        action=action,
        content_type=content_type,
        object_id=object_id,
        object_repr=object_repr,
        old_values=old_values or {},
        new_values=new_values or {},
        changes=changes,
        ip_address=ip,
        user_agent=user_agent,
        description=description,
    )
