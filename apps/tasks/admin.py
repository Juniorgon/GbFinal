from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'status', 'due_date', 'assigned_to', 'branch']
    list_filter = ['status', 'priority', 'branch']
    search_fields = ['title']
