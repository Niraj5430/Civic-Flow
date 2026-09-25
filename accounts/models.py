from django.db import models
from django.contrib.auth.models import User
from reports.models import Department

# The Profile model extends the default Django User.
# It's specifically used to link Department staff to their respective work units.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    civic_points = models.PositiveIntegerField(default=0)
    # If this user is a 'Department' staff member, this field tells us which one.
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    # Extra information about the user.
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
