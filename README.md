# Helpdesk & Ticket Management System

# helpdesk

Public repository: https://github.com/NewDaci/helpdesk

Helpdesk is a simple Django-based ticketing application demonstrating REST APIs, role-based permissions, Celery background tasks, and API documentation via drf-spectacular.

**Tech stack**
- Django
- Django REST Framework
- drf-spectacular (OpenAPI / Swagger)
- Celery (+ Redis broker)
- SQLite (default for development)

## 1. Clone repository

```bash
git clone https://github.com/NewDaci/helpdesk.git
cd helpdesk
```

## 2. Create and activate a virtual environment (zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Database migrations & admin user

```bash
cd helpdesk
python manage.py migrate
python manage.py createsuperuser
```

## 5. Run development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.
- API docs available at: `http://127.0.0.1:8000/api/docs/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`

## Celery (background tasks)

This project uses Celery for asynchronous tasks (escalations, scheduled jobs). Use Redis as the broker

### Install Redis (Ubuntu example)

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable --now redis
```

### Start a Celery worker

From the project root:

```bash
celery -A helpdesk worker --loglevel=info
```


Notes:
- The Celery app is defined in `helpdesk/helpdesk/celery.py` — the `-A helpdesk` flag points Celery at the Django project package.


---
project structure:

```
```zsh
$ tree  
.
├── helpdesk
│   ├── accounts
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations
│   │   │   ├── 0001_initial.py
│   │   │   └── __init__.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── signals.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── db.sqlite3
│   ├── helpdesk
│   │   ├── asgi.py
│   │   ├── celery.py
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── tickets
│       ├── admin.py
│       ├── apps.py
│       ├── __init__.py
│       ├── migrations
│       │   ├── 0001_initial.py
│       │   └── __init__.py
│       ├── models.py
│       ├── permissions.py
│       ├── serializers.py
│       ├── tasks.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── README.md
└── requirements.txt
```
7 directories, 34 files
