from rest_framework import serializers
from apps.finance.models import Transaction, Invoice, InvoiceItem, Category
from apps.documents.models import Document
from apps.notifications.models import Notification
from apps.users.models import User


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'get_full_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'category_type', 'icon', 'color', 'is_active']


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'title', 'description', 'amount', 'transaction_type', 'status',
            'category', 'category_name', 'date', 'reference', 'notes', 'currency',
            'tags', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'reference', 'created_by', 'created_at', 'updated_at']

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'total']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'client_email', 'client_address',
            'issue_date', 'due_date', 'status', 'subtotal', 'tax_rate', 'tax_amount',
            'discount', 'total', 'currency', 'notes', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'invoice_number', 'tax_amount', 'total', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file', 'document_type', 'status',
            'file_size', 'file_type', 'tags', 'uploaded_by', 'created_at'
        ]
        read_only_fields = ['id', 'file_size', 'file_type', 'uploaded_by', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'is_read',
            'action_url', 'action_label', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at']


class DashboardStatsSerializer(serializers.Serializer):
    revenues = serializers.FloatField()
    expenses = serializers.FloatField()
    profit = serializers.FloatField()
    transaction_count = serializers.IntegerField()
    pending_invoices = serializers.IntegerField()
    documents_count = serializers.IntegerField()
