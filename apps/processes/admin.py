from django.contrib import admin
from .models import Process, ProcessUpdate

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['number', 'client', 'type', 'status', 'value', 'branch']
    list_filter = ['status', 'type', 'branch']
    search_fields = ['number', 'client__name']

@admin.register(ProcessUpdate)
class ProcessUpdateAdmin(admin.ModelAdmin):
    list_display = ['process', 'title', 'date']
    list_filter = ['date']
