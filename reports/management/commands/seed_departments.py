from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from reports.models import Department
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Seed the database with initial Departments and Department users'

    def handle(self, *args, **options):
        department_group, _ = Group.objects.get_or_create(name='Department')

        departments = [
            {'name': 'Roads Department', 'description': 'Maintenance and repair of city roads and flyovers.'},
            {'name': 'Electricity Department', 'description': 'Managing street lights and public electrical infrastructure.'},
            {'name': 'Water Department', 'description': 'Handling water supply pipelines and public taps.'},
            {'name': 'Sewage Department', 'description': 'Maintenance of drainage systems and sewage lines.'},
            {'name': 'Cleaning Department', 'description': 'Sanitation, waste management and public area cleaning.'},
        ]

        created_departments = {}
        for dept in departments:
            obj, created = Department.objects.get_or_create(
                name=dept['name'],
                defaults={'description': dept['description']}
            )
            created_departments[dept['name']] = obj
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created department: {dept['name']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Department already exists: {dept['name']}"))

        department_accounts = [
            {'username': 'roads_dept', 'department': created_departments['Roads Department']},
            {'username': 'electricity_dept', 'department': created_departments['Electricity Department']},
            {'username': 'water_dept', 'department': created_departments['Water Department']},
            {'username': 'sewage_dept', 'department': created_departments['Sewage Department']},
            {'username': 'cleaning_dept', 'department': created_departments['Cleaning Department']},
        ]

        for account in department_accounts:
            user, created = User.objects.get_or_create(
                username=account['username'],
                defaults={'email': f"{account['username']}@example.com"}
            )
            user.set_password('password123')
            user.save()
            user.groups.clear()
            user.groups.add(department_group)

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.department = account['department']
            profile.save()

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created department user: {user.username} (password123)"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated department user: {user.username} (password reset to password123)"))
