import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from simple_history.models import HistoricalRecords
from decimal import Decimal


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = 'income', 'Revenu'
        EXPENSE = 'expense', 'Dépense'
        INVESTMENT = 'investment', 'Investissement'
        TRANSFER = 'transfer', 'Transfert'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CategoryType.choices)
    icon = models.CharField(max_length=50, default='tag')
    color = models.CharField(max_length=7, default='#2563EB')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='categories_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = 'income', 'Revenu'
        EXPENSE = 'expense', 'Dépense'
        INVESTMENT = 'investment', 'Investissement'
        SALARY = 'salary', 'Salaire'
        INVOICE = 'invoice', 'Facture'
        TRANSFER = 'transfer', 'Transfert'

    class Status(models.TextChoices):
        PENDING = 'pending', 'En attente'
        COMPLETED = 'completed', 'Complété'
        CANCELLED = 'cancelled', 'Annulé'
        FAILED = 'failed', 'Échoué'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=15, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transactions'
    )
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True, unique=True, null=True)
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='transactions/attachments/', null=True, blank=True)
    currency = models.CharField(max_length=10, default='FCFA')
    tags = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='transactions_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transactions_updated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.title} - {self.amount} {self.currency}"

    @property
    def is_income(self):
        return self.transaction_type in ['income', 'salary']

    @property
    def is_expense(self):
        return self.transaction_type in ['expense', 'invoice']

    def save(self, *args, **kwargs):
        if not self.reference:
            import random, string
            self.reference = 'TXN-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        super().save(*args, **kwargs)


class Invoice(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Brouillon'
        PENDING = 'pending', 'En attente'
        PAID = 'paid', 'Payé'
        OVERDUE = 'overdue', 'En retard'
        CANCELLED = 'cancelled', 'Annulé'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True)
    client_name = models.CharField(max_length=200)
    client_email = models.EmailField(blank=True)
    client_address = models.TextField(blank=True)
    client_phone = models.CharField(max_length=20, blank=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default='FCFA')
    notes = models.TextField(blank=True)
    terms = models.TextField(blank=True)
    transaction = models.OneToOneField(
        Transaction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='invoice'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='invoices_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-issue_date']

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.client_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            year = timezone.now().year
            count = Invoice.objects.filter(created_at__year=year).count() + 1
            self.invoice_number = f"INV-{year}-{count:04d}"
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total = self.subtotal + self.tax_amount - self.discount
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=300)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    total = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = 'Ligne de facture'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity}"


class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    alert_threshold = models.IntegerField(default=80, help_text="% d'utilisation pour alerte")
    is_settled = models.BooleanField(default=False)
    settled_at = models.DateTimeField(null=True, blank=True)
    settled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budgets_settled'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Budget'
        verbose_name_plural = 'Budgets'

    def __str__(self):
        return f"{self.name} - {self.amount} FCFA"

    @property
    def spent(self):
        from django.db.models import Sum
        result = Transaction.objects.filter(
            category=self.category,
            date__range=[self.period_start, self.period_end],
            transaction_type__in=['expense', 'invoice']
        ).aggregate(total=Sum('amount'))
        return result['total'] or Decimal('0')

    @property
    def remaining(self):
        return self.amount - self.spent

    @property
    def is_over_budget(self):
        return self.spent > self.amount

    @property
    def usage_percentage(self):
        if self.amount > 0:
            return min(int((self.spent / self.amount) * 100), 100)
        return 0


class BudgetRequest(models.Model):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'En attente'
        APPROVED = 'approved', 'Approuvé'
        REJECTED = 'rejected', 'Rejeté'

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title        = models.CharField(max_length=200)
    description  = models.TextField(blank=True)
    amount       = models.DecimalField(max_digits=15, decimal_places=2)
    category     = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budget_requests')
    period_start = models.DateField()
    period_end   = models.DateField(null=True, blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budget_requests'
    )
    reviewed_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='budget_requests_reviewed'
    )
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    budget       = models.OneToOneField(
        'Budget', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='from_request'
    )
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Demande de budget'
        verbose_name_plural = 'Demandes de budget'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.requested_by} ({self.get_status_display()})"


class CaisseMovement(models.Model):
    class MovementType(models.TextChoices):
        CREDIT = 'credit', 'Entrée de fonds'
        DEBIT  = 'debit',  'Dépense'

    id              = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movement_type   = models.CharField(max_length=10, choices=MovementType.choices)
    amount          = models.DecimalField(max_digits=15, decimal_places=2,
                                          validators=[MinValueValidator(Decimal('0.01'))])
    description     = models.CharField(max_length=300)
    transaction     = models.OneToOneField(
        Transaction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='caisse_movement'
    )
    created_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Mouvement de caisse'
        verbose_name_plural = 'Mouvements de caisse'
        ordering            = ['-created_at']

    def __str__(self):
        sign = '+' if self.movement_type == 'credit' else '-'
        return f"{sign}{self.amount} FCFA — {self.description}"

    # ── class-level helpers ──────────────────────────────────────────
    @classmethod
    def get_balance(cls):
        from django.db.models import Sum
        credits = cls.objects.filter(movement_type='credit').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        debits  = cls.objects.filter(movement_type='debit' ).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        return credits - debits

    @classmethod
    def credit(cls, amount, description, user, transaction=None):
        return cls.objects.create(
            movement_type='credit', amount=amount,
            description=description, created_by=user, transaction=transaction
        )

    @classmethod
    def debit(cls, amount, description, user, transaction=None):
        return cls.objects.create(
            movement_type='debit', amount=amount,
            description=description, created_by=user, transaction=transaction
        )
