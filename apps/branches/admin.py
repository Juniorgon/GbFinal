from django.contrib import admin
from .models import Branch

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'phone', 'admin_name', 'is_active']
    list_filter = ['is_active', 'state']
    search_fields = ['name', 'city', 'admin_name']
