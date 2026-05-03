from django.contrib import admin
from .models import Lawyer

@admin.register(Lawyer)
class LawyerAdmin(admin.ModelAdmin):
    list_display = ['name', 'oab_display', 'email', 'phone', 'branch', 'is_active']
    list_filter = ['is_active', 'oab_state', 'branch']
    search_fields = ['name', 'email', 'oab_number']
    filter_horizontal = ['accessible_branches']
