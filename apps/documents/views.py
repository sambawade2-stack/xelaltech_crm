from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Document
from .forms import DocumentForm
from apps.audit.utils import log_action
from apps.audit.models import AuditLog


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'documents/list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        qs = Document.objects.filter(status='active').select_related('uploaded_by')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(tags__icontains=q))
        doc_type = self.request.GET.get('type')
        if doc_type:
            qs = qs.filter(document_type=doc_type)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['document_types'] = Document.DocumentType.choices
        ctx['total_docs'] = Document.objects.filter(status='active').count()
        return ctx


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/form.html'
    success_url = reverse_lazy('documents:list')

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        log_action(
            user=self.request.user,
            action=AuditLog.ActionType.CREATE,
            instance=self.object,
            description=f"{self.request.user} a uploadé le document: {self.object.title}",
            request=self.request,
        )
        messages.success(self.request, f"Document '{self.object.title}' uploadé avec succès.")
        return response


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/detail.html'
    context_object_name = 'document'


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    success_url = reverse_lazy('documents:list')
    template_name = 'documents/confirm_delete.html'

    def form_valid(self, form):
        self.object.status = 'deleted'
        self.object.save()
        messages.success(self.request, "Document supprimé.")
        return super().form_valid(form)
