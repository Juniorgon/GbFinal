from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'cpf_cnpj', 'phone', 'city', 'branch', 'is_active']
    list_filter = ['type', 'branch', 'is_active']
    search_fields = ['name', 'cpf_cnpj', 'phone', 'email']
