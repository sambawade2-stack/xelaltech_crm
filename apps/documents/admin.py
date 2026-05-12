from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Document


@admin.register(Document)
class DocumentAdmin(SimpleHistoryAdmin):
    list_display = ['title', 'document_type', 'status', 'file_size_display', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'status']
    search_fields = ['title', 'tags']
