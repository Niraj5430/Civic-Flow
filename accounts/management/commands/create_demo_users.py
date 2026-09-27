from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from accounts.models import Profile
from reports.models import Department


class Command(BaseCommand):
    help = "Create demo users, groups, department and profiles for Civic Flow"

    def handle(self, *args, **options):

        # ---------------------------------------------------------
        # 1. Create Groups
        # ---------------------------------------------------------
        citizen_group, _ = Group.objects.get_or_create(name="Citizen")
        corporation_group, _ = Group.objects.get_or_create(name="Corporation")
        department_group, _ = Group.objects.get_or_create(name="Department")

        self.stdout.write(
            self.style.SUCCESS("✓ User groups ready")
        )

        # ---------------------------------------------------------
        # 2. Create Demo Department
        # ---------------------------------------------------------
        department, created = Department.objects.get_or_create(
            name="Water Supply"
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created demo department: Water Supply")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ Water Supply department already exists")
            )

        # ---------------------------------------------------------
        # Helper function for users
        # ---------------------------------------------------------
        def create_user(username, password, group):
            user, created = User.objects.get_or_create(
                username=username
            )

            if created:
                user.set_password(password)
                user.save()

            user.groups.add(group)

            return user, created

        # ---------------------------------------------------------
        # 3. Citizen
        # ---------------------------------------------------------
        citizen, created = create_user(
            "demo_citizen",
            "DemoCitizen@123",
            citizen_group
        )

        Profile.objects.get_or_create(user=citizen)

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created demo citizen")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ Demo citizen already exists")
            )

        # ---------------------------------------------------------
        # 4. Corporation
        # ---------------------------------------------------------
        corporation, created = create_user(
            "demo_corporation",
            "DemoCorporation@123",
            corporation_group
        )

        Profile.objects.get_or_create(user=corporation)

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created demo corporation")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ Demo corporation already exists")
            )

        # ---------------------------------------------------------
        # 5. Department
        # ---------------------------------------------------------
        department_user, created = create_user(
            "demo_department",
            "DemoDepartment@123",
            department_group
        )

        profile, _ = Profile.objects.get_or_create(
            user=department_user
        )

        profile.department = department
        profile.save()

        if created:
            self.stdout.write(
                self.style.SUCCESS("✓ Created demo department user")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✓ Demo department user already exists")
            )

        # ---------------------------------------------------------
        # Finished
        # ---------------------------------------------------------
        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Civic Flow demo accounts are ready!"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=============================================="
            )
        )

        self.stdout.write("")
        self.stdout.write("Citizen:")
        self.stdout.write("  Username: demo_citizen")
        self.stdout.write("  Password: DemoCitizen@123")

        self.stdout.write("")
        self.stdout.write("Corporation:")
        self.stdout.write("  Username: demo_corporation")
        self.stdout.write("  Password: DemoCorporation@123")

        self.stdout.write("")
        self.stdout.write("Department:")
        self.stdout.write("  Username: demo_department")
        self.stdout.write("  Password: DemoDepartment@123")
        self.stdout.write("  Department: Water Supply")

        self.stdout.write("")