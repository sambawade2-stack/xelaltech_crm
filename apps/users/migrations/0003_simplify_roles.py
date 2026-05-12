from django.db import migrations


ROLE_MAP = {
    'accountant': 'comptable',
    'manager':    'admin',
    'auditor':    'admin',
    'employee':   'membre',
}


def forward(apps, schema_editor):
    User = apps.get_model('users', 'User')
    for old, new in ROLE_MAP.items():
        User.objects.filter(role=old).update(role=new)


def backward(apps, schema_editor):
    pass  # one-way migration


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_add_company_settings'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
