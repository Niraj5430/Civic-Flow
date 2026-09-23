from django.contrib import admin
from .models import Profile

admin.site.site_header = "CivicFlow Administration"
admin.site.site_title = "CivicFlow Admin Portal"
admin.site.index_title = "Welcome to CivicFlow Dashboard"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('user__username', 'user__email')
