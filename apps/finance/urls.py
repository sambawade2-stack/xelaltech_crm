from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Page finance unifiée (transactions + factures)
    path('', views.FinanceView.as_view(), name='index'),

    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction_list'),
    path('transactions/new/', views.TransactionCreateView.as_view(), name='transaction_create'),
    path('transactions/<uuid:pk>/', views.TransactionDetailView.as_view(), name='transaction_detail'),
    path('transactions/<uuid:pk>/edit/', views.TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<uuid:pk>/delete/', views.TransactionDeleteView.as_view(), name='transaction_delete'),

    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/new/', views.InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<uuid:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<uuid:pk>/pdf/', views.InvoicePDFView.as_view(), name='invoice_pdf'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),

    # Budgets
    path('budgets/', views.BudgetListView.as_view(), name='budget_list'),
    path('budgets/new/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<uuid:pk>/settle/', views.BudgetSettleView.as_view(), name='budget_settle'),
    path('budgets/<uuid:pk>/expense/', views.BudgetExpenseView.as_view(), name='budget_expense'),
    path('caisse/deposit/', views.CaisseDepositView.as_view(), name='caisse_deposit'),

    # Demandes de budget
    path('budget-requests/', views.BudgetRequestListView.as_view(), name='budget_requests'),
    path('budget-requests/new/', views.BudgetRequestCreateView.as_view(), name='budget_request_create'),
    path('budget-requests/<uuid:pk>/approve/', views.BudgetRequestApproveView.as_view(), name='budget_request_approve'),
    path('budget-requests/<uuid:pk>/reject/', views.BudgetRequestRejectView.as_view(), name='budget_request_reject'),
]
