# Helpdesk & Ticket Management System

## Tech Stack
- Django
- Django REST Framework
- JWT Authentication
- Celery + Redis
- SQLite
- drf-spectacular

## Setup Instructions

### 1. Clone Repository
```bash
git clone <repo-url>
cd helpdesk
```

## Features
- User Authentication & Roles
- Ticket Management
- Search & Filtering
- Escalation System (Celery + Redis)
- Role-based Permissions
- Swagger API Documentation

## Run Project
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
celery -A helpdesk worker -l info
celery -A helpdesk beat -l info


### Bonus Features
- Ticket comments (threaded updates per ticket)
- Reporting API for tickets opened, resolved, and escalated in last 7 days
