from django.db import models
from django.contrib.auth.models import User

# This model represents the different Working Departments (e.g., Road, Electricity, Water).
class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# The primary model for any issue reported by a citizen.
# It tracks the life-cycle of a report from 'Reported' to 'Resolved'.
class Issue(models.Model):
    # These choices define the workflow states of an issue.
    STATUS_CHOICES = [
        ('REPORTED', 'Reported'),      # First stage: Citizen has submitted the report.
        ('ASSIGNED', 'Assigned'),      # Second stage: Corp has assigned a department.
        ('IN_PROGRESS', 'In Progress'),# Third stage: Dept has started working on it.
        ('COMPLETED', 'Completed'),    # Fourth stage: Dept has uploaded the 'After' photo.
        ('RESOLVED', 'Resolved'),      # Final stage: Corp has verified and closed the issue.
        ('REJECTED', 'Rejected'),      # Alternative: Corp has rejected the work and sent it back.
    ]
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_issues') # The Citizen
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_by_corp')
    
    # Content Fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    image_before = models.ImageField(upload_to='issues/before/') # Evidence of the problem
    image_after = models.ImageField(upload_to='issues/after/', null=True, blank=True) # Evidence of the fix
    location = models.CharField(max_length=255) # Manual address/location description
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')
    
    # Timing and Coordinates
    assigned_at = models.DateTimeField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=12, decimal_places=9, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Safely gets the URL for the 'Before' image, returns None if image missing.
    @property
    def image_before_url(self):
        try:
            return self.image_before.url
        except ValueError:
            return None

    # Safely gets the URL for the 'After' image, returns None if not yet uploaded.
    @property
    def image_after_url(self):
        try:
            return self.image_after.url
        except (ValueError, AttributeError):
            return None

    # Helper function to get the detail page link for this specific issue.
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('issue_detail', args=[str(self.id)])

    def __str__(self):
        return f"{self.title} - {self.status}"


# This model powers the 'Transparency Timeline'. 
# It creates a permanent record every time someone updates an issue.
class IssueHistory(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20) # What the status became
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Who made the change
    note = models.TextField(blank=True) # Optional reason/note
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp'] # Latest updates appear first

    def __str__(self):
        return f"{self.issue.title} - {self.status} at {self.timestamp}"


# Stores the feedback provided by a citizen after the work is COMPLETED.
class IssueReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)] # 1 to 5 Stars

    issue = models.OneToOneField(Issue, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews') # The Citizen
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, help_text="Optional: describe your experience")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for #{self.issue_id} — {self.rating}★"
