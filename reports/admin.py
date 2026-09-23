from django.contrib import admin
from .models import Issue, Department

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'department', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'location')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
