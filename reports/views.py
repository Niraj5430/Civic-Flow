from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q

from reports.services.civic_points import award_report_points
from .models import Issue, Department, IssueHistory, IssueReview
from .forms import IssueCreateForm, IssueCompleteForm, AssignIssueForm, DepartmentForm, IssueReviewForm

# The Public Landing Page
def home(request):
    from django.db.models import Q

    # Fetch real statistics for the 'CivicFlow in Action' section
    stats = {
        'total':      Issue.objects.count(),
        'resolved':   Issue.objects.filter(status='RESOLVED').count(),
        'in_progress': Issue.objects.filter(status='IN_PROGRESS').count(),
        'rejected':   Issue.objects.filter(status='REJECTED').count(),
    }

    # Handle Search functionality
    query = request.GET.get('q', '').strip()
    if query:
        recent_issues = Issue.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        ).order_by('-created_at')[:20]
    else:
        recent_issues = Issue.objects.order_by('-created_at')[:10]

    return render(request, 'home.html', {
        'stats': stats,
        'recent_issues': recent_issues,
        'query': query,
        # Feature descriptions for the 'Why CivicFlow?' section
        'features': [
            (" Smart Location", "Use GPS or autocomplete to pinpoint issues with precision.", "location-marker"),
            (" Duplicate Detection", "We warn you if a similar issue is already reported nearby.", "search-circle"),
            (" Full Transparency", "Every status change is logged and visible to all parties.", "refresh"),
            (" Photo Evidence", "Before & after images keep the process honest and accountable.", "photograph"),
            (" Citizen Reviews", "Rate the quality of the fix once your issue is resolved.", "star"),
            (" Department Routing", "Issues are routed to the right team — Roads, Water, Electricity & more.", "office-building"),
        ],
    })

# The central hub for all users after logging in.
# It detects the user's role and serves the correct dashboard.
@login_required
def dashboard(request):
    user = request.user
    is_corp = user.groups.filter(name='Corporation').exists()
    is_dept = user.groups.filter(name='Department').exists()

    # CORPORATION DASHBOARD
    if is_corp:
        status_filter = request.GET.get('status', '')
        dept_filter = request.GET.get('department', '')
        query = request.GET.get('q', '').strip()
        issues = Issue.objects.all().order_by('-created_at')
        if status_filter:
            issues = issues.filter(status=status_filter)
        if dept_filter:
            issues = issues.filter(department_id=dept_filter)
        if query:
            issues = issues.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        
        # Calculate summary numbers for the top cards
        stats = {
            'reported': issues.filter(status='REPORTED').count(),
            'in_progress': issues.filter(status='IN_PROGRESS').count(),
            'completed': issues.filter(status='COMPLETED').count(),
            'resolved': issues.filter(status='RESOLVED').count(),
        }
        
        template = 'reports/corp_dashboard.html'
        return render(request, template, {
            'issues': issues,
            'status_choices': Issue.STATUS_CHOICES,
            'stats': stats,
            'query': query,
            'departments': Department.objects.all(),
            'dept_filter': dept_filter,
        })

    # DEPARTMENT DASHBOARD
    elif is_dept:
        # Each Dept user is linked to a specific Department (e.g., Road Dept)
        user_dept = getattr(getattr(user, 'profile', None), 'department', None)
        status_filter = request.GET.get('status', '')
        department_status_choices = [
            ('ASSIGNED', 'Assigned'),
            ('COMPLETED', 'Completed'),
            ('RESOLVED', 'Resolved'),
        ]

        if user_dept:
            issues = Issue.objects.filter(department=user_dept)
            if status_filter in {choice[0] for choice in department_status_choices}:
                issues = issues.filter(status=status_filter)
            issues = issues.order_by('-updated_at')
        else:
            issues = Issue.objects.none()
            messages.warning(request, "You are not assigned to any department. Please contact an administrator.")

        return render(request, 'reports/ward_dashboard.html', {
            'issues': issues,
            'status_choices': department_status_choices,
            'status_filter': status_filter,
        })

    # CITIZEN DASHBOARD
    else:
        issues = Issue.objects.filter(user=user).order_by('-created_at')
        # Look for issues that are COMPLETED but don't have a review yet to show the alert.
        pending_reviews = issues.filter(status='COMPLETED').exclude(review__isnull=False)
        pending_reviews_count = pending_reviews.count()
        first_pending_issue = pending_reviews.first()
        
        return render(request, 'reports/citizen_dashboard.html', {
            'issues': issues,
            'pending_reviews_count': pending_reviews_count,
            'first_pending_issue_id': first_pending_issue.id if first_pending_issue else None
        })

# Allows Citizens to report a new issue.
@login_required
def create_issue(request):
    user = request.user

    # Safety Check: Corporation and Dept staff shouldn't report issues themselves.
    if user.groups.filter(name__in=['Corporation', 'Department']).exists():
        messages.error(
            request,
            "You are not allowed to report issues. Only Citizens can create reports."
        )
        return redirect('dashboard')

    if request.method == 'POST':
        form = IssueCreateForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                issue = form.save(commit=False)
                issue.user = user
                issue.status = 'REPORTED'
                issue.save()

                from reports.services.civic_points import award_report_points
                award_report_points(issue)
                # Log this action in the history timeline
                IssueHistory.objects.create(
                    issue=issue,
                    status='REPORTED',
                    actor=user,
                    note="Issue reported by citizen."
                )

                # -------------------------------------------------
                # AI ANALYSIS
                # -------------------------------------------------
                # AI failure MUST NOT prevent the report from being
                # successfully submitted.
                try:
                    from reports.services.ai_service import analyze_issue

                    analyze_issue(issue)

                except Exception as ai_error:
                    # Log AI failure but do not fail the citizen's report.
                    import logging
                    logging.getLogger(__name__).exception(
                        "AI analysis failed for issue %s: %s",
                        issue.id,
                        ai_error
                    )

                messages.success(
                    request,
                    "Issue submitted successfully! We'll review it shortly."
                )

                return redirect('dashboard')

            except Exception:
                messages.error(
                    request,
                    "Something went wrong while submitting the issue. "
                    "Please try again."
                )

        else:
            # If form is invalid, collect exact errors and show them clearly.
            error_list = []

            for field, errors in form.errors.items():
                field_name = field.replace('_', ' ').title()

                for error in errors:
                    error_list.append(
                        f"{field_name}: {error}"
                    )

            error_msg = (
                "Please correct errors: "
                + " | ".join(error_list)
                if error_list
                else "Check required fields."
            )

            messages.error(request, error_msg)

    else:
        form = IssueCreateForm()

    return render(
        request,
        'reports/create_issue.html',
        {'form': form}
    )
# Detailed view for a single issue.
# Detailed view for a single issue.
def issue_detail(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    user = request.user

    # Determine user permissions
    is_corp = (
        user.is_authenticated
        and user.groups.filter(name='Corporation').exists()
    )

    is_dept = (
        user.is_authenticated
        and user.groups.filter(name='Department').exists()
    )

    user_dept = (
        getattr(getattr(user, 'profile', None), 'department', None)
        if user.is_authenticated
        else None
    )

    # Privacy Protection
    if not user.is_authenticated and issue.status != 'RESOLVED':
        messages.info(request, "Please log in to view this issue.")
        return redirect('login')

    # Permission check
    if user.is_authenticated:
        can_view = (
            is_corp
            or (is_dept and issue.department == user_dept)
            or (issue.user == user)
            or issue.status == 'RESOLVED'
        )

        if not can_view:
            messages.error(
                request,
                "You are not allowed to access this page."
            )
            return redirect('dashboard')

    # Existing assignment form
    assign_form = (
        AssignIssueForm(instance=issue)
        if is_corp and issue.status in ['REPORTED', 'REJECTED']
        else None
    )

    # ---------------------------------------------------------
    # AI ANALYSIS
    # ---------------------------------------------------------

    ai_analysis = getattr(issue, 'ai_analysis', None)

    # Review logic
    existing_review = getattr(issue, 'review', None)

    review_form = None

    if (
        user.is_authenticated
        and issue.status in ['COMPLETED', 'RESOLVED']
        and issue.user == user
        and not existing_review
    ):
        review_form = IssueReviewForm()

    return render(request, 'reports/issue_detail.html', {
    'issue': issue,
    'assign_form': assign_form,
    'is_corp': is_corp,
    'is_dept': is_dept,
    'user_dept': user_dept,
    'ai_analysis': getattr(issue, 'ai_analysis', None),
    'history': issue.history.all().order_by('timestamp'),
    'existing_review': existing_review,
    'review_form': review_form,
})
# Corporation uses this to assign an issue to a specialized Department.
@login_required
def assign_issue(request, pk):
    if not request.user.groups.filter(name='Corporation').exists():
        messages.error(request, "Only Corporation managers can assign issues.")
        return redirect('dashboard')

    issue = get_object_or_404(Issue, pk=pk)

    if issue.status not in ('REPORTED', 'REJECTED'):
        messages.error(
            request,
            "This issue has already been assigned or is in another state."
        )
        return redirect('issue_detail', pk=pk)

    if request.method == 'POST':
        form = AssignIssueForm(request.POST, instance=issue)

        if form.is_valid():
            try:
                issue = form.save(commit=False)

                # Safety check: department must actually be selected
                if not issue.department:
                    messages.error(
                        request,
                        "Please select a department before assigning the issue."
                    )
                    return redirect('issue_detail', pk=pk)

                issue.status = 'ASSIGNED'
                issue.assigned_by = request.user
                issue.assigned_at = timezone.now()
                issue.save()

                # Award +5 Civic Points for successful assignment
                from reports.services.civic_points import award_assignment_points
                award_assignment_points(issue)

                # Log assignment in history
                IssueHistory.objects.create(
                    issue=issue,
                    status='ASSIGNED',
                    actor=request.user,
                    note=f"Assigned to {issue.department.name} by Corporation."
                )

                messages.success(
                    request,
                    f"Issue successfully assigned to {issue.department.name}."
                )

            except Exception:
                messages.error(
                    request,
                    "Assignment failed. Please try again."
                )

        else:
            messages.error(
                request,
                "Please select a valid department."
            )

    return redirect('issue_detail', pk=pk)

# Automatically assign an issue to the AI-recommended department.
@login_required
def auto_assign_issue(request, pk):
    # Only Corporation users can auto-assign
    if not request.user.groups.filter(name='Corporation').exists():
        messages.error(request, "Only Corporation managers can auto-assign issues.")
        return redirect('dashboard')

    issue = get_object_or_404(Issue, pk=pk)

    # Only unassigned/rejected issues can be assigned
    if issue.status not in ('REPORTED', 'REJECTED'):
        messages.error(request, "This issue cannot be assigned in its current state.")
        return redirect('issue_detail', pk=pk)

    # Get AI analysis
    ai_analysis = getattr(issue, 'ai_analysis', None)

    # Make sure a successful AI recommendation exists
    if not ai_analysis or not ai_analysis.is_successful:
        messages.error(request, "No successful AI recommendation is available.")
        return redirect('issue_detail', pk=pk)

    # Make sure AI selected a department
    if not ai_analysis.suggested_department:
        messages.error(request, "AI did not recommend a department.")
        return redirect('issue_detail', pk=pk)

    # Safety threshold
    if ai_analysis.department_confidence is None or ai_analysis.department_confidence < 0.75:
        messages.error(request, "AI confidence is below the 75% auto-assignment threshold.")
        return redirect('issue_detail', pk=pk)

    try:
        # Assign the AI-recommended department
        issue.department = ai_analysis.suggested_department
        issue.status = 'ASSIGNED'
        issue.assigned_by = request.user
        issue.assigned_at = timezone.now()
        issue.save()

        # Record assignment in history
        IssueHistory.objects.create(
            issue=issue,
            status='ASSIGNED',
            actor=request.user,
            note=(
                f"Automatically assigned to "
                f"{issue.department.name} using AI recommendation "
                f"({ai_analysis.department_confidence:.0%} confidence)."
            )
        )

        messages.success(
            request,
            f"Issue automatically assigned to {issue.department.name}."
        )

    except Exception:
        messages.error(
            request,
            "Automatic assignment failed. Please try manual assignment."
        )

    return redirect('issue_detail', pk=pk)

# The Main Workflow Engine: Handles Start, Complete, Approve, and Reject actions.
@login_required
def update_status(request, pk, action):
    issue = get_object_or_404(Issue, pk=pk)
    user = request.user
    is_corp = user.groups.filter(name='Corporation').exists()
    is_dept = user.groups.filter(name='Department').exists()
    user_dept = getattr(getattr(user, 'profile', None), 'department', None)

    # ACTIONS FOR DEPARTMENT USERS
    if is_dept:
        if issue.department != user_dept:
            messages.error(
                request,
                "This issue is not assigned to your department."
            )
            return redirect('dashboard')

        # Start: Assigned -> In Progress
        if action == 'start':
            if issue.status not in ('ASSIGNED', 'REJECTED'):
                messages.error(
                    request,
                    "Invalid status for starting work."
                )
            else:
                issue.status = 'IN_PROGRESS'
                issue.save()

                IssueHistory.objects.create(
                    issue=issue,
                    status='IN_PROGRESS',
                    actor=user,
                    note="Department started work."
                )

                messages.success(request, "Work started!")

            return redirect('issue_detail', pk=pk)

        # Complete: In Progress -> Completed
        elif action == 'complete':
            if request.method == 'POST':
                form = IssueCompleteForm(
                    request.POST,
                    request.FILES,
                    instance=issue
                )

                if form.is_valid():
                    completed = form.save(commit=False)
                    completed.status = 'COMPLETED'
                    completed.save()

                    IssueHistory.objects.create(
                        issue=completed,
                        status='COMPLETED',
                        actor=user,
                        note="Work finished. After photo uploaded."
                    )

                    messages.success(
                        request,
                        "Work marked as Completed. Awaiting final verification."
                    )

                    return redirect('issue_detail', pk=pk)

                else:
                    messages.error(
                        request,
                        "Please upload the Proof/After image."
                    )

            else:
                form = IssueCompleteForm(instance=issue)

            return render(
                request,
                'reports/complete_issue.html',
                {
                    'form': form,
                    'issue': issue
                }
            )

        else:
            messages.error(request, "Invalid action.")
            return redirect('issue_detail', pk=pk)

    # ACTIONS FOR CORPORATION USERS
    elif is_corp:

        if issue.status != 'COMPLETED':
            messages.error(
                request,
                "Cannot verify — issue must be Completed first."
            )
            return redirect('issue_detail', pk=pk)

        if request.method != 'POST':
            return redirect('issue_detail', pk=pk)

        # APPROVE: Completed -> Resolved
        if action == 'approve':
            issue.status = 'RESOLVED'
            issue.save()

            # Award +10 Civic Points for resolving the issue
            from reports.services.civic_points import award_resolution_points
            award_resolution_points(issue)

            IssueHistory.objects.create(
                issue=issue,
                status='RESOLVED',
                actor=user,
                note="Corp approved the fix."
            )

            messages.success(
                request,
                "Issue Resolved successfully!"
            )

        # REJECT: Completed -> Rejected
        elif action == 'reject':
            issue.status = 'REJECTED'
            issue.save()

            IssueHistory.objects.create(
                issue=issue,
                status='REJECTED',
                actor=user,
                note="Corp rejected the fix for rework."
            )

            messages.warning(
                request,
                "Fix rejected and sent back for re-work."
            )

        else:
            messages.error(request, "Invalid action.")
            return redirect('issue_detail', pk=pk)

    else:
        messages.error(
            request,
            "You are not allowed to perform this action."
        )
        return redirect('dashboard')

    return redirect('issue_detail', pk=pk)
# Allows Corporation to create new Working Departments.
@login_required
def create_ward(request):
    """Create a new Department (kept as create_ward for URL compatibility)."""
    if not request.user.groups.filter(name='Corporation').exists():
        messages.error(request, "You are not allowed to access this page.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "New department created successfully!")
                return redirect('dashboard')
            except Exception:
                messages.error(request, "Something went wrong. Department could not be created.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = DepartmentForm()
    return render(request, 'reports/create_ward.html', {'form': form})

# Special function: detects if a similar issue is being reported to prevent duplicates.
def check_duplicate(request):
    title = request.GET.get('title', '').strip()
    location = request.GET.get('location', '').strip()

    if not title and not location:
        return JsonResponse({'duplicates': []})

    qs = Issue.objects.exclude(status='RESOLVED')
    filters = Q()
    if title:
        filters |= Q(title__icontains=title)
    if location:
        filters |= Q(location__icontains=location)
    similar = qs.filter(filters).order_by('-created_at')[:5]
    
    data = [
        {
            'id': i.id,
            'title': i.title,
            'location': i.location,
            'status': i.get_status_display(),
            'date': i.created_at.strftime('%b %d, %Y'),
            'url': i.get_absolute_url(),
        }
        for i in similar
    ]
    return JsonResponse({'duplicates': data})

# Saves the citizen's rating and comment.
@login_required
def submit_review(request, pk):
    issue = get_object_or_404(Issue, pk=pk)

    if issue.status not in ['COMPLETED', 'RESOLVED']:
        messages.error(
            request,
            "Reviews can only be submitted for completed or resolved issues."
        )
        return redirect('issue_detail', pk=pk)

    if issue.user != request.user:
        messages.error(
            request,
            "Only the citizen who reported this issue can submit a review."
        )
        return redirect('issue_detail', pk=pk)

    if hasattr(issue, 'review'):
        messages.info(
            request,
            "You have already submitted a review for this issue."
        )
        return redirect('issue_detail', pk=pk)

    if request.method == 'POST':
        form = IssueReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.issue = issue
            review.reviewer = request.user
            review.save()

            # Award +5 Civic Points for submitting a review
            from reports.services.civic_points import award_review_points
            award_review_points(issue)

            messages.success(
                request,
                "Thank you for your feedback! Your review has been submitted."
            )
        else:
            messages.error(
                request,
                "Please provide a valid rating to submit your review."
            )

    return redirect('issue_detail', pk=pk)