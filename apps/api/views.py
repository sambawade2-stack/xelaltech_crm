from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal

from apps.finance.models import Transaction, Invoice, Category
from apps.documents.models import Document
from apps.notifications.models import Notification
from .serializers import (
    TransactionSerializer, InvoiceSerializer, CategorySerializer,
    DocumentSerializer, NotificationSerializer, DashboardStatsSerializer
)


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title', 'reference', 'description']
    ordering_fields = ['date', 'amount', 'created_at']
    filterset_fields = ['transaction_type', 'status', 'category']

    def get_queryset(self):
        return Transaction.objects.select_related('category', 'created_by').order_by('-date')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        qs = self.get_queryset()
        return Response({
            'total_revenues': qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0,
            'total_expenses': qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0,
            'count': qs.count(),
        })


class InvoiceViewSet(viewsets.ModelViewSet):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['invoice_number', 'client_name']
    filterset_fields = ['status']

    def get_queryset(self):
        return Invoice.objects.select_related('created_by').order_by('-issue_date')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['title', 'tags']
    filterset_fields = ['document_type', 'status']

    def get_queryset(self):
        return Document.objects.filter(status='active').select_related('uploaded_by')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'patch', 'delete']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'ok'})


class TokenObtainView(TokenObtainPairView):
    pass


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        first_day = now.replace(day=1)
        qs = Transaction.objects.filter(date__gte=first_day.date(), status='completed')
        revenues = float(qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0)
        expenses = float(qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0)
        return Response({
            'revenues': revenues,
            'expenses': expenses,
            'profit': revenues - expenses,
            'transaction_count': qs.count(),
            'pending_invoices': Invoice.objects.filter(status='pending').count(),
            'documents_count': Document.objects.filter(status='active').count(),
        })
