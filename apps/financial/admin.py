from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['type', 'description', 'value', 'status', 'due_date', 'branch']
    list_filter = ['type', 'status', 'branch']
    search_fields = ['description']
