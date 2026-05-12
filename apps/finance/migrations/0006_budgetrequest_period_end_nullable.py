from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0005_budget_request'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budgetrequest',
            name='period_end',
            field=models.DateField(blank=True, null=True),
        ),
    ]
