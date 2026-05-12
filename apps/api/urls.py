from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('transactions', views.TransactionViewSet, basename='transaction')
router.register('invoices', views.InvoiceViewSet, basename='invoice')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('documents', views.DocumentViewSet, basename='document')
router.register('notifications', views.NotificationViewSet, basename='notification')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', views.TokenObtainView.as_view(), name='token_obtain'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
]
