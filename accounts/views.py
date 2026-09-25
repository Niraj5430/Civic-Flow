from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import Group
from django.contrib import messages
from .forms import UserRegistrationForm, ManualPasswordResetForm

# Handles the creation of new Citizen accounts.
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # 1. Create the base User object
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()

                # 2. Create the associated Profile for extra data like phone_number
                from .models import Profile
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.phone_number = form.cleaned_data['phone_number']
                profile.save()

                # 3. Automatically assign every new registration to the 'Citizen' group
                citizen_group, _ = Group.objects.get_or_create(name='Citizen')
                user.groups.add(citizen_group)

                # 4. Log them in and say hello
                login(request, user)
                messages.success(request, f"Welcome to CivicFlow, {user.first_name or user.username}! Your account has been created.")
                return redirect('dashboard')
            except Exception:
                messages.error(request, "Something went wrong while creating your account. Please try again.")
        else:
            # Display detailed errors if registration fails (e.g., password too short)
            for field, errors in form.errors.items():
                for error in errors:
                    label = (form.fields[field].label or field.replace('_', ' ').title()) if field != '__all__' else "Error"
                    messages.error(request, f"{label}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


# Standard Login view.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, 'accounts/login.html')

        # authenticate() checks the credentials against the database.
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user) # login() creates the session for the user
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            # If they were redirected here from a protected page, send them back there.
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            return render(request, 'accounts/login.html', {'username': username})

    return render(request, 'accounts/login.html')


# Standard Logout view.
def logout_view(request):
    if request.method == 'POST':
        logout(request) # Clears the session and logs the user out.
        messages.success(request, "You have been logged out successfully.")
        return redirect('home')
    return redirect('dashboard')


def manual_password_reset(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ManualPasswordResetForm(request.POST)
        if form.is_valid():
            user = form.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, 'Your password has been updated. Please log in with your new password.')
            return redirect('login')
    else:
        form = ManualPasswordResetForm()

    return render(request, 'accounts/password_reset_manual.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from reports.models import Issue


@login_required
def profile(request):
    user = request.user

    profile = user.profile

    issues = Issue.objects.filter(user=user)

    total_reports = issues.count()
    resolved_reports = issues.filter(status='RESOLVED').count()
    completed_reports = issues.filter(status='COMPLETED').count()

    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'completed_reports': completed_reports,
    })