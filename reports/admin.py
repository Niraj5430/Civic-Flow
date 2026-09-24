from django.contrib import admin
from .models import Issue, Department
from .models import Issue, Department, IssueAIAnalysis

class IssueAIAnalysisInline(admin.StackedInline):
    model = IssueAIAnalysis
    extra = 0
    readonly_fields = (
        'suggested_department', 'department_confidence', 'department_reasoning',
        'is_image_relevant', 'image_confidence', 'image_explanation', 'detected_problem',
        'model_name', 'raw_response', 'is_successful', 'error_message', 'created_at'
    )
    can_delete = False

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'department', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description', 'location')
    inlines = [IssueAIAnalysisInline]

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(IssueAIAnalysis)
class IssueAIAnalysisAdmin(admin.ModelAdmin):
    list_display = ('issue', 'suggested_department', 'department_confidence', 'is_image_relevant', 'is_successful', 'created_at')
    list_filter = ('is_successful', 'is_image_relevant', 'suggested_department', 'created_at')
    search_fields = ('issue__title', 'department_reasoning', 'detected_problem')
    readonly_fields = ('created_at',)

