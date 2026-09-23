from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# A simple helper function to test if our custom 500 error page works.
def trigger_500(request):
    raise Exception("This is a deliberate 500 error for testing.")

urlpatterns = [
    # The standard Django Admin interface (/admin)
    path('admin/', admin.site.urls),
    
    # We 'include' the URLs from our two apps to keep things organized.
    path('', include('reports.urls')),          # Home, Dashboards, and Reports
    path('accounts/', include('accounts.urls')), # Login, Register, Logout
    
    # Test routes: you can visit /500/ to see your custom error page.
    path('500/', trigger_500),
]

# ----- SPECIAL FILE SERVING LOGIC -----
# This part ensures that images (media) and CSS (static) work even when DEBUG=False.
from django.views.static import serve
from django.urls import re_path

if settings.DEBUG:
    # Standard development way to serve files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Manual serving: This allows you to test the 'Production' feel (custom error pages)
    # on your local machine while still seeing the uploaded images.
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    
    # Automatically serve static folders if they are defined in settings.
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        for static_dir in settings.STATICFILES_DIRS:
            if static_dir.exists():
                urlpatterns += [
                    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': static_dir}),
                ]

