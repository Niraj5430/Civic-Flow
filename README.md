# Civic Flow

Civic Flow is a web-based civic issue reporting and management platform built with Django.

Citizens can report civic problems, Corporation users can review and assign issues to the appropriate department, and Department users can work on assigned issues, upload proof of completion, and submit the work for Corporation verification.

The platform also uses AI to recommend the appropriate department based on the reported issue.

---

## Features

### Citizen

- Create civic issue reports
- Upload issue images
- Provide issue location and description
- Track issue status
- View issue history and timeline
- View assigned department
- Submit reviews for completed/resolved issues
- Earn Civic Points

### Corporation

- View all reported issues
- Filter issues by status
- Filter issues by department
- View complete issue details
- View AI department recommendations
- Accept AI recommendations
- Manually assign issues to departments
- Reassign rejected issues
- Verify completed work
- Approve department work
- Reject department work and request rework
- View citizen reviews

### Department

- View issues assigned to the department
- Start work on assigned issues
- Move issues to `IN_PROGRESS`
- Upload an "After" image as proof of completion
- Mark issues as completed
- Rework rejected issues

### AI Assistance

Civic Flow uses Google's Gemini API to analyze reported civic issues.

The AI can:

- Detect the reported problem
- Recommend an appropriate department
- Provide a confidence score
- Provide reasoning for the recommendation

AI recommendations are assistance only. The Corporation retains control over the final department assignment.

### Civic Points

Citizens can earn Civic Points through participation in the civic reporting workflow.

Civic Points are stored as part of the user's profile and can be displayed as part of the citizen profile.

---

## Issue Workflow

```text
Citizen Reports Issue
        |
        v
     REPORTED
        |
        v
AI Analysis / Department Recommendation
        |
        v
Corporation Reviews Recommendation
        |
        v
Corporation Assigns Department
        |
        v
      ASSIGNED
        |
        v
Department Starts Work
        |
        v
    IN_PROGRESS
        |
        v
Department Uploads After Image
        |
        v
     COMPLETED
        |
        v
Corporation Verification
       / \
      /   \
 Reject   Approve
   |         |
   v         v
REJECTED   RESOLVED
   |
   v
Department Reworks Issue


Technology Stack
Backend
Python
Django
Django ORM
PostgreSQL
Frontend
HTML
Tailwind CSS
JavaScript
AI
Google Gemini API
Gemini Flash model
Development Tools
Git
GitHub
VS Code
Python Virtual Environment
Project Structure
civic-flow/
│
├── accounts/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_demo_users.py
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
│
├── reports/
│   ├── migrations/
│   ├── services/
│   ├── templates/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── ...
│
├── civic_flow/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── media/
│
├── static/
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
Installation
1. Clone the Repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd civic-flow
2. Create a Virtual Environment
Windows
python -m venv .venv

Activate it:

.\.venv\Scripts\activate
Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
3. Install Dependencies
pip install -r requirements.txt
4. Configure Environment Variables

Create a .env file in the project root.

Use .env.example as a template.

Example:

POSTGRES_DB=civicflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

GEMINI_API_KEY=your_gemini_api_key

Do not commit your real .env file to GitHub.

5. Apply Database Migrations
python manage.py migrate
6. Create Demo Accounts

Civic Flow includes a custom Django management command for creating demo accounts.

Run:

python manage.py create_demo_users

This creates the required demo users, groups, department, and department-user association.

7. Start the Development Server
python manage.py runserver

Open:

http://127.0.0.1:8000/
Environment Variables

Civic Flow uses environment variables for database and AI configuration.

Create a .env file containing the required values.

POSTGRES_DB=civicflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

GEMINI_API_KEY=your_gemini_api_key

The repository should contain:

.env.example

but the actual:

.env

file should remain local and should not be committed to GitHub.

Important

Never publish:

PostgreSQL passwords
Gemini API keys
Django secret keys
Personal credentials
Production credentials
User Roles

Civic Flow contains three main user roles.

Citizen

Citizens can:

Create civic issue reports
Upload issue images
Add descriptions
Provide location information
Track their issues
View issue history
View assigned departments
Submit reviews
Earn Civic Points
Corporation

Corporation users can:

View all issues
Review reported issues
View AI recommendations
Accept AI recommendations
Manually assign departments
Reassign rejected issues
Verify completed work
Approve completed work
Reject completed work
View citizen reviews
Department

Department users are associated with a specific department.

They can:

View issues assigned to their department
Start work
Move issues to IN_PROGRESS
Upload completion evidence
Mark issues as COMPLETED
Rework rejected issues
Demo Accounts

Civic Flow provides a management command to automatically create demo accounts for local development and testing.

Run:

python manage.py create_demo_users

The command creates the required groups, demo users, department, and department-user association.

Demo Roles
Username	Role	Department
demo_citizen	Citizen	—
demo_corporation	Corporation	—
demo_department	Department	Water Supply

The Department demo account is automatically connected to the Water Supply department.

The command can be run multiple times without intentionally creating duplicate demo accounts.

Security: Demo accounts are intended only for local development and testing. Do not use demo credentials in production.

AI Department Recommendation

When a citizen reports an issue, Civic Flow can send the issue information to the Gemini API for analysis.

The AI can provide:

Suggested Department
Confidence
Detected Problem
Reasoning

For example:

Suggested Department:
Water Supply

Confidence:
95%

Detected Problem:
Flooding caused by a water leak from a tank

Reasoning:
The issue appears to involve a water leak from a tank,
which corresponds to the Water Supply department.

The AI recommendation does not automatically replace Corporation control.

The Corporation can review the recommendation and:

Accept the recommended department
Manually select another department
Use Auto Assign when the configured confidence requirement is satisfied
AI Configuration

AI configuration is controlled through the Django settings and environment variables.

The Gemini API key should be provided through:

GEMINI_API_KEY=your_gemini_api_key

AI-related settings can include:

AI_ENABLED
AI_AUTO_ASSIGN
AI_CONFIDENCE_THRESHOLD
AI_TIMEOUT_SECONDS
AI_MODEL

The AI system is designed to provide department recommendations and supporting information while keeping the final assignment under Corporation control.

Civic Points

Civic Flow includes a Civic Points system for citizen participation.

Each user profile can contain a Civic Points value.

Example:

Civic Points: 10

Civic Points can be used to recognize participation in the civic reporting workflow.

The system can be extended in the future with:

Points history
Achievement levels
Leaderboards
Badges
Participation statistics
Issue Statuses
Status	Meaning
REPORTED	Citizen has submitted an issue
ASSIGNED	Corporation has assigned the issue to a department
IN_PROGRESS	Department has started working
COMPLETED	Department has completed the work and submitted proof
RESOLVED	Corporation has approved the completed work
REJECTED	Corporation has rejected the submitted work and requested rework
Issue History

Civic Flow maintains an issue history/timeline.

Major actions are recorded, including:

Issue reported
Department assigned
Work started
Work completed
Issue approved
Issue rejected

This provides a transparent record of the issue lifecycle.

Citizen Reviews

After an issue reaches the appropriate completed/resolved stage, the citizen who originally reported the issue can submit a review.

A review can contain:

Rating
Optional comment

Corporation users can view citizen reviews when reviewing completed work.

Testing the Complete Workflow

The complete application workflow can be tested using the demo accounts.

Step 1 — Citizen

Login as:

demo_citizen

Create a civic issue with:

Title
Description
Location
Image

The issue starts as:

REPORTED
Step 2 — Corporation

Login as:

demo_corporation

The Corporation can:

View the reported issue
Open the issue details
View the AI recommendation
Review confidence and reasoning
Accept the recommendation or manually select a department
Assign the issue

The issue becomes:

ASSIGNED
Step 3 — Department

Login as:

demo_department

The assigned issue appears in the Department dashboard.

The Department can:

Start work
Move the issue to IN_PROGRESS
Complete the work
Upload an "After" image

The issue becomes:

COMPLETED
Step 4 — Corporation Verification

Login again as:

demo_corporation

Review the completed issue.

The Corporation can:

Approve

The issue becomes:

RESOLVED
Reject

The issue becomes:

REJECTED

The Department can then rework the issue.

Step 5 — Citizen Review

The Citizen can view the completed/resolved issue and submit a rating and optional comment.

Useful Django Commands
Start Development Server
python manage.py runserver
Create Migrations
python manage.py makemigrations
Apply Migrations
python manage.py migrate
Create Superuser
python manage.py createsuperuser
Create Demo Accounts
python manage.py create_demo_users
Check Project Configuration
python manage.py check
Run Tests
python manage.py test
Security Notes

Before deploying Civic Flow to production:

Set DEBUG=False
Configure ALLOWED_HOSTS
Use strong database credentials
Use a secure Django SECRET_KEY
Keep .env outside version control
Never expose API keys
Never use demo credentials in production
Configure secure database access
Configure HTTPS
Review authentication and authorization permissions
Configure production static and media file handling
Git and GitHub Workflow

After completing a meaningful development phase, check the changed files:

git status

Add the intended changes:

git add .

Commit:

git commit -m "Describe the completed change"

Push:

git push

Example:

git commit -m "Add Civic Points and demo account setup"

For future development, meaningful completed phases should be committed separately so the project history remains understandable.

Development Guidelines

When modifying Civic Flow:

Make one logical feature/change at a time.
Test the feature locally.
Run Django checks.
Check migrations.
Review git status.
Commit the completed phase.
Push the commit to GitHub.

Useful checks:

python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py test
Project Status
Implemented
Citizen registration/login
Corporation login
Department login
Role-based access
Civic issue reporting
Image upload
Location information
Issue status tracking
Issue history/timeline
Corporation dashboard
Department dashboard
Citizen dashboard
Corporation-to-department assignment
Manual department assignment
AI department recommendation
AI confidence score
AI reasoning
AI-assisted assignment
Automatic assignment
Department workflow
Completion image upload
Corporation verification
Issue rejection and rework
Citizen reviews
Civic Points
User profiles
Demo account creation command
Future Improvements

Possible future improvements include:

Civic Points history
Civic Points leaderboard
Citizen badges and achievements
Advanced issue analytics
Geographic issue heatmaps
Email notifications
In-app notifications
Improved AI image analysis
Corporation analytics dashboard
Advanced reporting
Automated testing
Production deployment
Improved role and permission management
License

This project is currently developed for educational and project purposes.

