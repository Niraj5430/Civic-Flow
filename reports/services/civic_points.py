from accounts.models import Profile


def award_civic_points(user, points):
    """
    Safely add Civic Points to a user's profile.
    """
    if not user or not user.is_authenticated:
        return

    profile, _ = Profile.objects.get_or_create(user=user)

    profile.civic_points += points
    profile.save(update_fields=["civic_points"])


def award_report_points(issue):
    """
    +10 points when a citizen successfully submits a report.
    """
    if issue.user:
        award_civic_points(issue.user, 10)


def award_assignment_points(issue):
    """
    +5 points when Corporation assigns the report to a department.
    """
    if issue.user:
        award_civic_points(issue.user, 5)


def award_resolution_points(issue):
    """
    +10 points when Corporation finally resolves the report.
    """
    if issue.user:
        award_civic_points(issue.user, 10)


def award_review_points(issue):
    """
    +5 points when the citizen submits a review.
    """
    if issue.user:
        award_civic_points(issue.user, 5)