from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from reports.models import Issue, Department
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Seeds database with simplified 3-role setup'

    def handle(self, *args, **kwargs):
        # 1. Create Groups
        roles = ['Citizen', 'Corporation', 'Department']
        for role in roles:
            Group.objects.get_or_create(name=role)
        
        self.stdout.write("Groups created.")

        # 1b. Create Departments
        road_dept, _ = Department.objects.get_or_create(name="Road Department", defaults={'description': "Handles road repairs and pavement."})
        water_dept, _ = Department.objects.get_or_create(name="Water Department", defaults={'description': "Handles water leaks and plumbing."})
        elect_dept, _ = Department.objects.get_or_create(name="Electrical Department", defaults={'description': "Handles street lights and power."})

        # 2. Create Sample Users
        def create_user(username, role):
            u, created = User.objects.get_or_create(username=username, email=f"{username}@example.com")
            if created:
                u.set_password('password123')
            u.groups.clear()
            u.groups.add(Group.objects.get(name=role))
            u.save()
            return u

        citizen = create_user('citizen_user', 'Citizen')
        dept_user = create_user('dept_user', 'Department')
        corp = create_user('municipal_corporation', 'Corporation')

        # Link Department User to Road Department
        from accounts.models import Profile
        profile, _ = Profile.objects.get_or_create(user=dept_user)
        profile.department = road_dept
        profile.save()
        
        self.stdout.write("Users created (pw: password123) and Department User linked to Road Dept.")

        # 3. Sample Issues
        Issue.objects.get_or_create(
            title="Broken Pavement on Broadway",
            defaults={
                'user': citizen,
                'description': "Safety hazard near the entrance.",
                'location': "Broadway & 42nd",
                'status': 'REPORTED'
            }
        )
        
        Issue.objects.get_or_create(
            title="Water Leak",
            defaults={
                'user': citizen,
                'department': water_dept,
                'description': "Pipe burst in the garden.",
                'location': "Main Street Park",
                'status': 'IN_PROGRESS'
            }
        )

        self.stdout.write("Seed data complete.")
