from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Transaction, Invoice, InvoiceItem, Category, Budget


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'total']
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = ['invoice_number', 'client_name', 'status', 'total', 'due_date', 'created_at']
    list_filter = ['status']
    search_fields = ['invoice_number', 'client_name', 'client_email']
    inlines = [InvoiceItemInline]
    readonly_fields = ['invoice_number', 'tax_amount', 'total', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'transaction_type', 'amount', 'status', 'date', 'created_by']
    list_filter = ['transaction_type', 'status', 'category']
    search_fields = ['title', 'reference', 'description']
    readonly_fields = ['reference', 'created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(SimpleHistoryAdmin):
    list_display = ['name', 'category', 'amount', 'period_start', 'period_end']
    list_filter = ['category']
