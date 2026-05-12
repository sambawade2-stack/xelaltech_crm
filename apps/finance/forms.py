from django import forms
from django.forms import inlineformset_factory
from .models import Transaction, Invoice, InvoiceItem, Category, Budget


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'description', 'amount', 'transaction_type', 'status',
                  'category', 'date', 'notes', 'attachment', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Titre de la transaction'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'transaction_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tags séparés par des virgules'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['category'].empty_label = "-- Sélectionner une catégorie --"


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client_name', 'client_email', 'client_address', 'client_phone',
                  'issue_date', 'due_date', 'status', 'tax_rate', 'discount', 'notes', 'terms']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-input'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'client_address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'client_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'due_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'tax_rate': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'terms': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'quantity', 'unit_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
        }


InvoiceItemFormSet = inlineformset_factory(
    Invoice, InvoiceItem, form=InvoiceItemForm,
    extra=3, can_delete=True, min_num=1, validate_min=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'category_type', 'icon', 'color', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category_type': forms.Select(attrs={'class': 'form-select'}),
            'icon': forms.TextInput(attrs={'class': 'form-input'}),
            'color': forms.TextInput(attrs={'class': 'form-input', 'type': 'color'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'category', 'amount', 'period_start', 'period_end', 'alert_threshold']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'period_start': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'period_end': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
