from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'document_type', 'tags', 'related_transaction']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'file': forms.FileInput(attrs={'class': 'form-input'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tags séparés par virgule'}),
            'related_transaction': forms.Select(attrs={'class': 'form-select'}),
        }
