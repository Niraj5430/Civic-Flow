from django import forms
from .models import Issue, Department, IssueReview
from django.contrib.auth.models import User, Group

# Form used by Citizens to report a new problem.
# We include hidden fields for GPS coordinates which are filled by JavaScript.
class IssueCreateForm(forms.ModelForm):
    latitude = forms.DecimalField(required=False, widget=forms.HiddenInput())
    longitude = forms.DecimalField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Issue
        # We only ask for the essentials. The 'status' and 'user' are set in the view logic.
        fields = ['title', 'description', 'location', 'latitude', 'longitude', 'image_before']

# Form used by Department workers when they finish a fix.
# It forces them to upload an 'After' image as proof.
class IssueCompleteForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['image_after']
    
    # Custom validation: Ensure the image is actually provided.
    def clean_image_after(self):
        image = self.cleaned_data.get('image_after')
        if not image:
            raise forms.ValidationError("You must upload an AFTER image to complete the task.")
        return image

# Form used by Corporation to assign an issue to a Department.
class AssignIssueForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We populate the dropdown with all existing departments.
        self.fields['department'].queryset = Department.objects.all()
        self.fields['department'].empty_label = "Select a Department"

    class Meta:
        model = Issue
        fields = ['department']


# Simple form for creating new Working Departments (Corporation only).
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'description']


# Form for Citizens to rate the quality of a resolved issue.
class IssueReviewForm(forms.ModelForm):
    # Use RadioButtons (1-5) instead of a regular dropdown for better UX.
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.RadioSelect,
        label="Your Rating"
    )

    class Meta:
        model = IssueReview
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional — share your experience...'})
        }
