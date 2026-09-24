from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('issue/<int:pk>/', views.issue_detail, name='issue_detail'),
    
    # Dashboard & Reporting
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.create_issue, name='create_issue'),
    path('report/check-duplicate/', views.check_duplicate, name='check_duplicate'), # Used to warn about similar reports
    
    # Action endpoints (mostly for Corporation and Department)
    path('issue/<int:pk>/assign/', views.assign_issue, name='assign_issue'),
    path('issue/<int:pk>/auto-assign/',views.auto_assign_issue, name='auto_assign_issue'),
    path('issue/<int:pk>/status/<str:action>/', views.update_status, name='update_status'), # Universal status updater
    path('issue/<int:pk>/review/', views.submit_review, name='submit_review'), # For Citizen feedback
    
    # Management
    path('ward/create/', views.create_ward, name='create_ward'), # Corporation can create new Depts here
]
