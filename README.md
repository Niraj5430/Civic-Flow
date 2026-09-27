# Civic Flow

## AI-Assisted Civic Issue Reporting and Management Platform

Civic Flow is a Django-based civic issue management platform that connects citizens, municipal corporations, and departments through a centralized reporting and resolution workflow.

The platform allows citizens to report civic problems, corporations to review and manage reports, and departments to handle assigned issues. It also integrates Google Gemini for AI-assisted issue analysis while keeping final department assignment under human control.

---

## 🚀 Key Features

### 👤 Citizen

- Citizen registration and authentication
- Submit civic issues
- Add issue title and description
- Upload photographs of reported problems
- Provide issue location
- Track submitted issues
- View issue status
- View AI-generated analysis
- Citizen profile and civic points

### 🏢 Corporation

- Corporation authentication
- Corporation dashboard
- View reported civic issues
- Review issue details
- Review AI department recommendations
- Review AI confidence and reasoning
- Assign issues to appropriate departments
- Monitor issue progress

### 🏛️ Department

- Department-specific authentication
- Department dashboard
- View issues assigned to the department
- Review issue information and images
- Update issue status
- Track department workload

---

## 🤖 AI-Assisted Issue Analysis

Civic Flow integrates Google's Gemini API to assist with civic issue analysis.

The AI can:

- Recommend an appropriate department
- Generate department confidence
- Provide reasoning for the recommendation
- Determine whether an uploaded image is relevant to the complaint
- Generate image relevance confidence
- Detect the problem visible in the image
- Store the AI analysis for later review

### Human-Controlled Assignment

The AI operates in **suggestion-only mode**.

It does **not automatically assign or modify the department of an issue**.

The Corporation user reviews the AI recommendation and remains responsible for the final department assignment.

This design prevents an AI recommendation from directly changing the civic workflow.

---
## 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │     Citizen      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │  Django Web App  │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
        ┌───────────┐      ┌────────────┐      ┌─────────────┐
        │ Citizen   │      │ Corporation│      │ Department  │
        │ Workflow  │      │ Workflow   │      │ Workflow    │
        └───────────┘      └─────┬──────┘      └─────────────┘
                                 │
                                 ▼
                         ┌──────────────────┐
                         │    Gemini AI     │
                         │ Issue Analysis   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   PostgreSQL     │
                         └──────────────────┘

                    Containerized using Docker
                              │
                              ▼
                    GitHub Actions CI/CD
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
          Automated Tests            Docker Build
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    GitHub Container
                       Registry
```

## 🛠️ Technology Stack

| Category | Technology |
|---|---|
| Backend | Django 5.2 |
| Programming Language | Python 3.11 |
| Database | PostgreSQL 17 |
| AI | Google Gemini API |
| ORM | Django ORM |
| Frontend | Django Templates + Tailwind CSS |
| Containerization | Docker |
| Container Orchestration | Docker Compose |
| CI/CD | GitHub Actions |
| Container Registry | GitHub Container Registry |
| Version Control | Git + GitHub |

## 📁 Project Structure

```text
civic-flow/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── management/
│       └── commands/
│           └── create_demo_users.py
│
├── reports/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── services/
│   │   └── ai_service.py
│   ├── tests_ai.py
│   └── migrations/
│
├── civic_flow/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/
├── static/
├── media/
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
└── manage.py
```

## 🐳 Running with Docker

### Prerequisites

Install:

- Docker Desktop
- Git

### Clone the repository

```bash
git clone https://github.com/Niraj5430/Civic-Flow.git
cd Civic-Flow
```

### Start the application

```bash
docker compose up --build
```

The application will be available at:

```text
http://localhost:8000
```

Django runs inside the web container and PostgreSQL runs inside a separate database container.

## 🗄️ Database

Civic Flow uses PostgreSQL as its primary database.

Docker Compose provides the PostgreSQL container and the Django application connects to it using environment variables.

Typical configuration:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
```

Django migrations can be applied using:

```bash
docker compose exec web python manage.py migrate
```

## 👥 Demo Accounts

For demonstration and testing, the project includes a Django management command that creates the required groups, department, profiles, and demo users.

Run:

```bash
docker compose exec web python manage.py create_demo_users
```

This creates:

| Role | Username | Password |
|---|---|---|
| Citizen | `demo_citizen` | `DemoCitizen@123` |
| Corporation | `demo_corporation` | `DemoCorporation@123` |
| Department | `demo_department` | `DemoDepartment@123` |

The Department demo account is associated with:

**Water Supply**

These credentials are intended only for local/demo testing.

> **Security:** Real credentials, API keys, and secrets must never be committed to the repository.

## 🧪 Testing

Civic Flow includes automated Django tests for the AI functionality and AI analysis model.

### Current tests cover

- AI-disabled behavior
- Missing Gemini API key handling
- Successful AI classification
- Department recommendation validation
- Rejection of invalid/hallucinated department IDs
- Gemini API exception handling
- `IssueAIAnalysis` model creation

Run the test suite locally:

```bash
docker compose exec web python manage.py test
```

The test suite is also executed automatically by GitHub Actions.

## 🔄 CI/CD Pipeline

Civic Flow implements a CI/CD pipeline using GitHub Actions.

The workflow is defined in:

```text
.github/workflows/ci.yml
```

The pipeline runs automatically when code is pushed or a pull request is created for the configured branches.

### Continuous Integration

The CI process performs the following steps:

```text
Developer Push
      │
      ▼
GitHub Actions
      │
      ▼
Checkout Repository
      │
      ▼
Setup Python 3.11
      │
      ▼
Install Dependencies
      │
      ▼
Django System Checks
      │
      ▼
Run PostgreSQL 17
      │
      ▼
Run Django Migrations
      │
      ▼
Run Automated Tests
```

If the tests fail, the Docker publishing stage does not execute.

## 🐳 Automated Docker Build

After the Django test job succeeds, GitHub Actions automatically builds the Civic Flow Docker image.

```text
             Django Tests
                  │
                  │ PASS
                  ▼
           Docker Build
                  │
                  ▼
        Docker Image Created
                  │
                  ▼
      GitHub Container Registry
```

The Docker image is published to:

```text
ghcr.io/niraj5430/civic-flow
```

The workflow uses GitHub's built-in `GITHUB_TOKEN` for authentication with GitHub Container Registry.

Docker images are tagged using the Git commit SHA, allowing a published image to be traced back to the source-code version that created it.

## 🔁 CI/CD Workflow

The complete pipeline can be summarized as:

```text
Developer
    │
    ▼
Git Push
    │
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├─────────────────────────┐
    ▼                         ▼
Django Tests              PostgreSQL
    │
    ▼
Tests PASS
    │
    ▼
Docker Build
    │
    ▼
Docker Image
    │
    ▼
GitHub Container Registry
```

This provides automated validation and container image delivery whenever the configured workflow is triggered.

## 🤖 AI Service Architecture

The AI functionality is implemented in:

```text
reports/services/ai_service.py
```

The service:

- Retrieves available departments from PostgreSQL.
- Sends the civic issue information to Gemini.
- Includes the uploaded image when available.
- Requests structured JSON output.
- Validates the returned department ID.
- Normalizes confidence values.
- Stores the analysis in `IssueAIAnalysis`.
- Handles API and processing failures safely.

The AI does not directly modify the issue's assigned department.

## 🔐 AI Validation

Civic Flow does not blindly trust the AI response.

The returned department ID is checked against the actual departments available in the database.

For example:

### Database Departments

```text
1 → Roads Department
2 → Water Department
3 → Cleaning Department
```

If the AI returns:

```text
department_id = 99999
```

the response is rejected because that department does not exist in the database.

The system also handles:

- Missing Gemini API keys
- API failures
- Invalid department IDs
- Invalid AI responses
- Image loading errors
- Other AI processing exceptions

Failed analyses are recorded without crashing the main application workflow.

## ⚙️ Environment Variables

Sensitive configuration is supplied through environment variables.

Example configuration:

```text
SECRET_KEY
DEBUG

POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT

GEMINI_API_KEY
AI_MODE
AI_ENABLED
AI_AUTO_ASSIGN
AI_MODEL
AI_CONFIDENCE_THRESHOLD
AI_TIMEOUT_SECONDS
```

> **Security:** The Gemini API key must never be committed to GitHub.

## 🧠 AI Configuration

Example configuration:

```text
AI_MODE=demo
AI_ENABLED=True
AI_AUTO_ASSIGN=False
AI_CONFIDENCE_THRESHOLD=0.75
AI_TIMEOUT_SECONDS=10
```

The important setting is:

```text
AI_AUTO_ASSIGN=False
```

This keeps the AI in suggestion-only mode.

The Corporation user reviews the recommendation and makes the final assignment.

## 🔄 Civic Issue Workflow

```text
Citizen
   │
   ▼
Submit Civic Issue
   │
   ├── Title
   ├── Description
   ├── Location
   └── Image
   │
   ▼
PostgreSQL
   │
   ▼
Gemini AI Analysis
   │
   ├── Department Recommendation
   ├── Department Confidence
   ├── Department Reasoning
   ├── Image Relevance
   ├── Image Confidence
   └── Detected Problem
   │
   ▼
Corporation Review
   │
   ▼
Department Assignment
   │
   ▼
Department Handles Issue
   │
   ▼
Status Updates
   │
   ▼
Issue Resolution
```

## 🐳 Docker Services

Docker Compose runs Civic Flow using two primary services.

### Web

**`civic_flow_web`**

Runs the Django application.

### Database

**`civic_flow_db`**

Runs PostgreSQL 17.

### Architecture

```text
┌─────────────────────────────┐
│       civic_flow_web        │
│                             │
│       Django 5.2            │
│       Python 3.11           │
└──────────────┬──────────────┘
               │
               │ PostgreSQL
               ▼
┌─────────────────────────────┐
│        civic_flow_db        │
│                             │
│       PostgreSQL 17         │
└─────────────────────────────┘
```

### Check containers

```bash
docker compose ps
```

### Start the application

```bash
docker compose up
```

### Start with a fresh image build

```bash
docker compose up --build
```

### Stop containers

```bash
docker compose down
```

## 📋 Development Commands

### Check Django configuration

```bash
docker compose exec web python manage.py check
```

### Apply migrations

```bash
docker compose exec web python manage.py migrate
```

### Run tests

```bash
docker compose exec web python manage.py test
```

### Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Create demo users

```bash
docker compose exec web python manage.py create_demo_users
```

### Open Django shell

```bash
docker compose exec web python manage.py shell
```

## 📊 Project Highlights

### Application

- Role-based authentication
- Citizen issue reporting
- Corporation dashboard
- Department dashboard
- Civic issue tracking
- Image uploads
- Issue status management
- Citizen profiles
- Civic points

### AI

- Gemini API integration
- AI department recommendation
- Department confidence
- AI reasoning
- Image relevance analysis
- Image confidence
- Problem detection
- AI response validation
- Failure handling
- Human-controlled assignment

### DevOps

- PostgreSQL
- Docker
- Docker Compose
- Automated Django tests
- GitHub Actions
- CI/CD pipeline
- Docker image build automation
- GitHub Container Registry
- Commit-based Docker image tagging

## 🚀 Future Improvements

Possible future improvements include:

- Production deployment
- Cloud object storage for uploaded images
- Geographic issue hotspot visualization
- Email and notification system
- More comprehensive end-to-end testing
- Application monitoring
- Centralized logging
- Automated production deployment

## 👨‍💻 Author

**Niraj Sharma**

Civic Flow demonstrates the integration of:

```text
Django
+
PostgreSQL
+
Google Gemini AI
+
Docker
+
Docker Compose
+
Automated Testing
+
GitHub Actions
+
CI/CD
+
GitHub Container Registry
```

The project was developed as a portfolio project demonstrating full-stack development, AI integration, containerization, automated testing, and DevOps practices.

## 📄 License

This project is intended for educational, demonstration, and portfolio purposes.
