from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (ListView, DetailView, CreateView,
                                   UpdateView, DeleteView, TemplateView)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from django.views import View

from .models import Transaction, Invoice, InvoiceItem, Category, Budget, CaisseMovement, BudgetRequest
from .forms import TransactionForm, InvoiceForm, InvoiceItemFormSet, CategoryForm, BudgetForm
from apps.audit.utils import log_action
from apps.audit.models import AuditLog
from apps.users.mixins import FinanceRequiredMixin, AdminRequiredMixin


class TransactionListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'finance/transactions/list.html'
    context_object_name = 'transactions'
    paginate_by = 20

    def get_queryset(self):
        qs = Transaction.objects.select_related('category', 'created_by').order_by('-date', '-created_at')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(reference__icontains=q) | Q(description__icontains=q))
        t = self.request.GET.get('type')
        if t:
            qs = qs.filter(transaction_type=t)
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        cat = self.request.GET.get('category')
        if cat:
            qs = qs.filter(category_id=cat)
        date_from = self.request.GET.get('date_from')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        date_to = self.request.GET.get('date_to')
        if date_to:
            qs = qs.filter(date__lte=date_to)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        ctx['total_revenues'] = qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0
        ctx['total_expenses'] = qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0
        ctx['net_balance'] = ctx['total_revenues'] - ctx['total_expenses']
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['transaction_types'] = Transaction.TransactionType.choices
        ctx['status_choices'] = Transaction.Status.choices
        return ctx


class TransactionCreateView(FinanceRequiredMixin, CreateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transactions/form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action=AuditLog.ActionType.CREATE,
            instance=self.object,
            description=f"{self.request.user} a créé une transaction: {self.object.title} ({self.object.amount} FCFA)",
            request=self.request,
        )
        messages.success(self.request, f"Transaction '{self.object.title}' créée avec succès.")
        return response


class TransactionUpdateView(FinanceRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransactionForm
    template_name = 'finance/transactions/form.html'
    success_url = reverse_lazy('finance:transaction_list')

    def form_valid(self, form):
        old = Transaction.objects.get(pk=self.object.pk)
        old_values = {'title': old.title, 'amount': str(old.amount), 'status': old.status}
        response = super().form_valid(form)
        new_values = {'title': self.object.title, 'amount': str(self.object.amount), 'status': self.object.status}
        log_action(
            user=self.request.user,
            action=AuditLog.ActionType.UPDATE,
            instance=self.object,
            old_values=old_values,
            new_values=new_values,
            description=f"{self.request.user} a modifié la transaction: {self.object.title}",
            request=self.request,
        )
        messages.success(self.request, f"Transaction '{self.object.title}' mise à jour.")
        return response


class TransactionDeleteView(FinanceRequiredMixin, DeleteView):
    model = Transaction
    success_url = reverse_lazy('finance:transaction_list')
    template_name = 'finance/transactions/confirm_delete.html'

    def form_valid(self, form):
        log_action(
            user=self.request.user,
            action=AuditLog.ActionType.DELETE,
            instance=self.object,
            description=f"{self.request.user} a supprimé la transaction: {self.object.title} ({self.object.amount} FCFA)",
            request=self.request,
        )
        messages.success(self.request, "Transaction supprimée.")
        return super().form_valid(form)


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'finance/transactions/detail.html'
    context_object_name = 'transaction'


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'finance/invoices/list.html'
    context_object_name = 'invoices'
    paginate_by = 20

    def get_queryset(self):
        qs = Invoice.objects.select_related('created_by').order_by('-issue_date')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(invoice_number__icontains=q) | Q(client_name__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Invoice.Status.choices
        ctx['total_paid'] = Invoice.objects.filter(status='paid').aggregate(t=Sum('total'))['t'] or 0
        ctx['total_pending'] = Invoice.objects.filter(status='pending').aggregate(t=Sum('total'))['t'] or 0
        ctx['total_overdue'] = Invoice.objects.filter(status='overdue').aggregate(t=Sum('total'))['t'] or 0
        return ctx


class InvoiceCreateView(FinanceRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'finance/invoices/form.html'
    success_url = reverse_lazy('finance:invoice_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action=AuditLog.ActionType.CREATE,
            instance=self.object,
            description=f"{self.request.user} a créé la facture {self.object.invoice_number}",
            request=self.request,
        )
        messages.success(self.request, f"Facture {self.object.invoice_number} créée.")
        return response


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'finance/invoices/detail.html'
    context_object_name = 'invoice'


class InvoicePDFView(FinanceRequiredMixin, View):
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk)
        from apps.reports.utils import generate_invoice_pdf
        pdf_buffer = generate_invoice_pdf(invoice)
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture-{invoice.invoice_number}.pdf"'
        log_action(
            user=request.user,
            action=AuditLog.ActionType.EXPORT,
            instance=invoice,
            description=f"{request.user} a téléchargé la facture {invoice.invoice_number}",
            request=request,
        )
        return response


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'finance/categories/list.html'
    context_object_name = 'categories'


class BudgetListView(LoginRequiredMixin, ListView):
    model = Budget
    template_name = 'finance/budgets/list.html'
    context_object_name = 'budgets'

    def get_queryset(self):
        return Budget.objects.select_related('category', 'created_by').order_by('is_settled', '-period_start')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['transaction_types'] = Transaction.TransactionType.choices
        ctx['caisse_balance'] = CaisseMovement.get_balance()
        ctx['caisse_movements'] = CaisseMovement.objects.select_related('created_by')[:15]
        return ctx


class BudgetCreateView(FinanceRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance/budgets/form.html'
    success_url = reverse_lazy('finance:budget_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Budget créé avec succès.")
        return super().form_valid(form)


class BudgetSettleView(FinanceRequiredMixin, View):
    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        if not budget.is_settled:
            budget.is_settled = True
            budget.settled_at = timezone.now()
            budget.settled_by = request.user
            budget.save()
            messages.success(request, f"Budget « {budget.name} » soldé.")
        return redirect('finance:budget_list')


class BudgetExpenseView(LoginRequiredMixin, View):
    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        title = request.POST.get('title', '').strip()
        raw_amount = request.POST.get('amount', '0')
        date_str = request.POST.get('date', str(timezone.now().date()))
        notes = request.POST.get('notes', '')

        if not title or not raw_amount:
            messages.error(request, "Titre et montant sont requis.")
            return redirect('finance:budget_list')

        try:
            amount = Decimal(str(raw_amount))
        except Exception:
            messages.error(request, "Montant invalide.")
            return redirect('finance:budget_list')

        # Create the transaction
        txn = Transaction.objects.create(
            title=title,
            amount=amount,
            transaction_type='expense',
            category=budget.category,
            date=date_str,
            notes=notes,
            status='completed',
            created_by=request.user,
        )

        # Debit the caisse automatically
        balance = CaisseMovement.get_balance()
        CaisseMovement.debit(
            amount=amount,
            description=f"{title} (Budget: {budget.name})",
            user=request.user,
            transaction=txn,
        )
        new_balance = balance - amount

        if new_balance < 0:
            msg = (f"Dépense de {amount:,.0f} FCFA enregistrée. "
                   f"⚠️ Caisse en déficit : {new_balance:,.0f} FCFA")
            messages.warning(request, msg)
        else:
            messages.success(request, (
                f"Dépense de {amount:,.0f} FCFA débitée de la caisse. "
                f"Solde caisse : {new_balance:,.0f} FCFA"
            ))
        return redirect('finance:budget_list')


class CaisseDepositView(FinanceRequiredMixin, View):
    def post(self, request):
        raw_amount = request.POST.get('amount', '0')
        description = request.POST.get('description', 'Alimentation caisse').strip()

        try:
            amount = Decimal(str(raw_amount))
            if amount <= 0:
                raise ValueError
        except Exception:
            messages.error(request, "Montant invalide.")
            return redirect('finance:budget_list')

        label = description or 'Alimentation caisse'

        # Record as an income Transaction so it appears in financial stats
        txn = Transaction.objects.create(
            title=label,
            amount=amount,
            transaction_type='income',
            date=timezone.now().date(),
            status='completed',
            created_by=request.user,
        )

        CaisseMovement.credit(
            amount=amount,
            description=label,
            user=request.user,
            transaction=txn,
        )
        new_balance = CaisseMovement.get_balance()
        messages.success(request, (
            f"{amount:,.0f} FCFA ajoutés à la caisse. "
            f"Nouveau solde : {new_balance:,.0f} FCFA"
        ))
        return redirect('finance:budget_list')


class FinanceView(LoginRequiredMixin, TemplateView):
    template_name = 'finance/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Sum
        tab = self.request.GET.get('tab', 'transactions')
        ctx['tab'] = tab

        # Transactions
        txn_qs = Transaction.objects.select_related('category', 'created_by').order_by('-date', '-created_at')
        q = self.request.GET.get('q', '')
        if q:
            txn_qs = txn_qs.filter(Q(title__icontains=q) | Q(reference__icontains=q))
        ttype = self.request.GET.get('type', '')
        if ttype:
            txn_qs = txn_qs.filter(transaction_type=ttype)

        ctx['transactions'] = txn_qs[:50]
        ctx['total_revenues'] = txn_qs.filter(transaction_type__in=['income', 'salary']).aggregate(t=Sum('amount'))['t'] or 0
        ctx['total_expenses'] = txn_qs.filter(transaction_type__in=['expense', 'invoice']).aggregate(t=Sum('amount'))['t'] or 0
        ctx['net_balance'] = ctx['total_revenues'] - ctx['total_expenses']
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['transaction_types'] = Transaction.TransactionType.choices
        ctx['status_choices'] = Transaction.Status.choices

        # Invoices
        inv_qs = Invoice.objects.select_related('created_by').order_by('-issue_date')
        ctx['invoices'] = inv_qs[:30]
        ctx['total_paid'] = inv_qs.filter(status='paid').aggregate(t=Sum('total'))['t'] or 0
        ctx['total_pending'] = inv_qs.filter(status='pending').aggregate(t=Sum('total'))['t'] or 0
        ctx['status_choices_inv'] = Invoice.Status.choices

        return ctx


# ══════════════════ DEMANDES DE BUDGET ══════════════════

class BudgetRequestListView(LoginRequiredMixin, ListView):
    model = BudgetRequest
    template_name = 'finance/budget_requests/list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        user = self.request.user
        if user.can_access_finance:
            return BudgetRequest.objects.select_related('requested_by', 'category', 'reviewed_by').order_by('status', '-created_at')
        return BudgetRequest.objects.filter(requested_by=user).select_related('category').order_by('-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['pending_count'] = BudgetRequest.objects.filter(status='pending').count()
        ctx['categories'] = Category.objects.filter(is_active=True)
        return ctx


class BudgetRequestCreateView(LoginRequiredMixin, View):
    def post(self, request):
        title        = request.POST.get('title', '').strip()
        description  = request.POST.get('description', '').strip()
        raw_amount   = request.POST.get('amount', '0')
        category_id  = request.POST.get('category', '').strip()
        category_new = request.POST.get('category_new', '').strip()
        period_start = request.POST.get('period_start', '').strip()
        period_end   = request.POST.get('period_end', '').strip() or None

        if not all([title, raw_amount, period_start]):
            messages.error(request, "Intitulé, montant et date de début sont obligatoires.")
            return redirect('finance:budget_requests')

        try:
            amount = Decimal(str(raw_amount))
            if amount <= 0:
                raise ValueError
        except Exception:
            messages.error(request, "Montant invalide.")
            return redirect('finance:budget_requests')

        # Catégorie : existante ou nouvelle
        if category_id and category_id != 'new':
            category = get_object_or_404(Category, pk=category_id)
        elif category_new:
            category, _ = Category.objects.get_or_create(
                name__iexact=category_new,
                defaults={
                    'name': category_new,
                    'category_type': Category.CategoryType.EXPENSE,
                    'created_by': request.user,
                }
            )
        else:
            messages.error(request, "Veuillez sélectionner ou saisir une catégorie.")
            return redirect('finance:budget_requests')

        BudgetRequest.objects.create(
            title=title,
            description=description,
            amount=amount,
            category=category,
            period_start=period_start,
            period_end=period_end,
            requested_by=request.user,
        )
        messages.success(request, f"Demande « {title} » soumise. En attente d'approbation.")
        return redirect('finance:budget_requests')


class BudgetRequestApproveView(FinanceRequiredMixin, View):
    def post(self, request, pk):
        br = get_object_or_404(BudgetRequest, pk=pk, status='pending')
        notes = request.POST.get('notes', '').strip()

        # Si period_end non défini, on prend fin du mois de début
        from datetime import date
        import calendar
        period_end = br.period_end
        if not period_end:
            ps = br.period_start
            last_day = calendar.monthrange(ps.year, ps.month)[1]
            period_end = date(ps.year, ps.month, last_day)

        # Créer le budget réel
        budget = Budget.objects.create(
            name=br.title,
            category=br.category,
            amount=br.amount,
            period_start=br.period_start,
            period_end=period_end,
            created_by=request.user,
        )
        br.status      = 'approved'
        br.reviewed_by = request.user
        br.reviewed_at = timezone.now()
        br.review_notes = notes
        br.budget      = budget
        br.save()

        # Notifier le demandeur
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=br.requested_by,
            title="Demande de budget approuvée ✓",
            message=f"Votre demande « {br.title} » ({br.amount:,.0f} FCFA) a été approuvée.",
            notification_type='success',
            action_url='/finance/budgets/',
            action_label='Voir les budgets',
        )
        messages.success(request, f"Demande « {br.title} » approuvée. Budget créé.")
        return redirect('finance:budget_requests')


class BudgetRequestRejectView(FinanceRequiredMixin, View):
    def post(self, request, pk):
        br = get_object_or_404(BudgetRequest, pk=pk, status='pending')
        notes = request.POST.get('notes', '').strip()
        if not notes:
            messages.error(request, "Un motif de refus est requis.")
            return redirect('finance:budget_requests')

        br.status       = 'rejected'
        br.reviewed_by  = request.user
        br.reviewed_at  = timezone.now()
        br.review_notes = notes
        br.save()

        from apps.notifications.models import Notification
        Notification.objects.create(
            user=br.requested_by,
            title="Demande de budget refusée",
            message=f"Votre demande « {br.title} » a été refusée. Motif : {notes}",
            notification_type='warning',
            action_url='/finance/budget-requests/',
            action_label='Voir mes demandes',
        )
        messages.warning(request, f"Demande « {br.title} » refusée.")
        return redirect('finance:budget_requests')
