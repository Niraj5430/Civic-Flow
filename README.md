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
- Filter issues by status and department
- Search issues
- View complete issue details
- View AI department recommendations
- View AI confidence score and reasoning
- Accept AI recommendations
- Manually assign issues to departments
- Reassign rejected issues
- Verify completed work
- Approve or reject department work
- View citizen reviews

### Department

- View issues assigned to the department
- Start work on assigned issues
- Upload an "After" image as proof
- Mark issues as completed
- Handle rejected issues and perform rework

### AI Assistance

Civic Flow uses Google's Gemini API to analyze reported civic issues.

The AI can:

- Detect the reported problem
- Recommend an appropriate department
- Provide a confidence score
- Provide reasoning for the recommendation
- Analyze whether the uploaded image is relevant to the reported issue

AI recommendations are assistance only. The Corporation retains control over the final department assignment.

### Civic Points

Citizens can earn Civic Points through participation in the civic reporting workflow.

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
  Reject  Approve
    |        |
    v        v
REJECTED   RESOLVED
    |
    v
Department Reworks Issue
```

---

## Technology Stack

### Backend

- Python
- Django
- Django ORM
- PostgreSQL

### Frontend

- HTML
- Tailwind CSS
- JavaScript

### AI

- Google Gemini API
- Gemini Flash model

### Development Tools

- Git
- GitHub
- VS Code
- Python Virtual Environment

---

## Project Structure

```text
civic-flow/
│
├── accounts/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── create_demo_users.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── civic_flow/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── reports/
│   ├── migrations/
│   ├── services/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── media/
├── static/
├── templates/
│
├── .env
├── .env.example
├── .gitignore
├── db.sqlite3
├── manage.py
├── README.md
└── requirements.txt
```

---

## User Roles

Civic Flow has three main user roles.

### 1. Citizen

Citizens can:

- Register/login
- Report civic issues
- Upload images
- Provide location and description
- Track issue progress
- View the issue timeline
- View assigned department
- Submit reviews
- Earn Civic Points

### 2. Corporation

Corporation users manage the overall issue workflow.

They can:

- View reported issues
- Review AI recommendations
- Assign departments
- Reassign issues
- Verify completed work
- Approve or reject department work

### 3. Department

Department users handle issues assigned to their department.

They can:

- View assigned issues
- Start work
- Upload proof of completion
- Mark work as completed
- Rework rejected issues

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd civic-flow
```

Replace the repository URL with the actual GitHub repository URL.

---

### 2. Create a Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file in the project root.

Example:

```env
POSTGRES_DB=civicflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

GEMINI_API_KEY=your_gemini_api_key
```

### Important

Do not commit your real `.env` file to GitHub.

The `.env` file should remain private.

Use `.env.example` to show other developers which environment variables are required.

Example:

```env
POSTGRES_DB=civicflow
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change-me
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

GEMINI_API_KEY=your_gemini_api_key
```

---

## Database Setup

Make sure PostgreSQL is installed and running.

Create the database:

```sql
CREATE DATABASE civicflow;
```

Then run Django migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Create an Admin User

Create a Django superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:

- Username
- Email
- Password

Then start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

---

## Demo Accounts

For development/testing, the project includes a management command that can create demo users.

Run:

```bash
python manage.py create_demo_users
```

This creates the required demo users and role configuration for testing the Citizen, Corporation, and Department workflows.

### Important

The demo accounts are intended for local development/testing only.

Change or remove demo passwords before deploying the project publicly.

If the command is not used, users can also be created manually through the Django admin panel.

---

## Running the Project

Activate the virtual environment:

```powershell
.\.venv\Scripts\activate
```

Start the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

---

## AI Configuration

Civic Flow uses the Google Gemini API for AI-assisted issue analysis.

The AI layer can provide:

- Detected problem
- Suggested department
- Department confidence
- Explanation/reasoning
- Image relevance analysis

The Gemini API key is configured through the `.env` file.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The AI system is designed as a recommendation layer.

The Corporation user makes the final department assignment.

---

## AI Workflow

```text
Citizen Creates Report
        |
        v
Issue Submitted
        |
        v
Gemini AI Analysis
        |
        +----> Detect Problem
        |
        +----> Suggest Department
        |
        +----> Confidence Score
        |
        +----> Reasoning
        |
        +----> Image Relevance
        |
        v
Corporation Reviews Recommendation
        |
        v
Final Department Assignment
```

---

## Civic Points

Civic Flow includes a Civic Points system for citizen participation.

The user's Civic Points are stored in the account profile.

Points can be used to represent participation and engagement within the civic reporting workflow.

---

## Issue Statuses

The application uses the following main issue statuses:

| Status | Description |
|---|---|
| `REPORTED` | Citizen has submitted the issue |
| `ASSIGNED` | Corporation has assigned the issue to a department |
| `IN_PROGRESS` | Department has started working on the issue |
| `COMPLETED` | Department has completed the work and submitted proof |
| `RESOLVED` | Corporation has verified and approved the work |
| `REJECTED` | Corporation rejected the submitted work and requested rework |

---

## Issue History

Each important workflow action is recorded in the issue history.

Examples include:

- Issue reported
- Department assigned
- Work started
- Work completed
- Issue rejected
- Issue resolved

This provides a transparency timeline that allows citizens and administrators to track the progress of an issue.

---

## Image Uploads

Citizens can upload an image showing the reported problem.

Departments can upload an "After" image as proof that the issue has been addressed.

Uploaded media is stored through Django's media configuration.

For production deployments, configure appropriate persistent media storage.

---

## Security Notes

Before deploying Civic Flow to production:

- Do not commit `.env`
- Use a strong Django `SECRET_KEY`
- Use a production PostgreSQL database
- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Configure secure HTTPS settings
- Protect uploaded media
- Use strong passwords
- Replace development/demo credentials
- Keep API keys private

---

## Development

Useful Django commands:

### Create migrations

```bash
python manage.py makemigrations
```

### Apply migrations

```bash
python manage.py migrate
```

### Create superuser

```bash
python manage.py createsuperuser
```

### Run development server

```bash
python manage.py runserver
```

### Check Django configuration

```bash
python manage.py check
```

### Run tests

```bash
python manage.py test
```

---

## Git Workflow

After completing a meaningful working phase:

```bash
git status
```

Review the changes:

```bash
git diff
```

Add the changes:

```bash
git add .
```

Commit:

```bash
git commit -m "Describe the completed change"
```

Push:

```bash
git push
```

Use clear commit messages that describe the completed feature or fix.

Examples:

```bash
git commit -m "Add civic points system"
```

```bash
git commit -m "Add AI department recommendations"
```

```bash
git commit -m "Add issue verification workflow"
```

---

## Current Development Status

The core Civic Flow workflow is implemented:

- Citizen issue reporting
- Issue tracking
- Corporation dashboard
- Department dashboard
- Department assignment
- AI department recommendation
- AI confidence and reasoning
- Issue status workflow
- Department work workflow
- After-image proof
- Corporation verification
- Issue rejection and rework
- Issue history/timeline
- Citizen reviews
- Civic Points
- User profiles
- Role-based access

---

## Future Improvements

Possible future improvements include:

- Notifications
- Email alerts
- Real-time issue updates
- Civic Points leaderboard
- More detailed analytics
- Location-based issue hotspots
- Advanced AI image analysis
- Production cloud deployment
- Automated testing expansion
- API development
- Mobile application

---

## License

This project is currently intended for educational, portfolio, and development purposes.

Add an appropriate open-source license before distributing the project under a formal open-source license.

---

## Author

Civic Flow

Built with Django, PostgreSQL, Tailwind CSS, and Google Gemini AI.