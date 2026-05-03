from django.contrib import admin
from .models import Contract

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'type', 'total_value', 'status', 'branch']
    list_filter = ['status', 'type', 'branch']
    search_fields = ['title', 'client__name']
