# Patient Management System — Setup Guide

**Complete guide (roles, dev workflow, security):** [FULL_DOCUMENTATION.md](FULL_DOCUMENTATION.md)

## Project structure

```
shiab/
└── Simple Patient Management System/
├── manage.py              # Django entry point
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── README.md              # Quick start (root)
│
├── config/                # Project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── views.py           # Dashboard view
│
├── apps/                  # Django applications
│   ├── accounts/          # Login & staff roles (UserProfile)
│   ├── patients/          # Patient CRUD & search
│   ├── appointments/      # Appointments & status workflow
│   └── billing/           # Invoices, payments, void/cancel
│
├── templates/
│   ├── accounts/          # Login page
│   ├── base.html
│   ├── dashboard.html
│   ├── patients/
│   ├── appointments/
│   └── billing/
│
├── static/                # Static assets (CSS, JS)
├── tests/                 # Test suite
├── docs/                  # Documentation
├── scripts/               # Helper scripts
└── data/                  # SQLite DB (when USE_SQLITE=1)
```

## Staff login & roles

- **Sign in:** http://127.0.0.1:8000/accounts/login/ (anonymous users are redirected here).
- **Super admin:** Create with `python manage.py createsuperuser`. Full app + **Admin** link to Django `/admin/` for user and role management.
- **Clinic roles** (set under **Admin → Users → Clinic role**):
  - **Clinic admin** — all modules (patients, appointments, billing).
  - **Reception** — patients & appointments only (no invoices list).
  - **Billing** — invoices & payments only (no patient add/edit).
  - **Viewer** — read-only everywhere.

## Install & run

```powershell
cd "C:\shiab\Simple Patient Management System"
python -m venv ..\.venv
..\.venv\Scripts\activate
pip install -r requirements.txt
```

### PostgreSQL

```sql
CREATE DATABASE clinic_db;
```

```powershell
$env:DB_NAME="clinic_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="your_password"
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
```

### SQLite (local dev)

```powershell
$env:USE_SQLITE="1"
```

### Migrate & run

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Run tests

```powershell
$env:USE_SQLITE="1"
python manage.py test tests
```

## URL map

| URL | Feature |
|-----|---------|
| `/accounts/login/` | Staff sign-in |
| `/patients/` | Patient list + search |
| `/patients/create/` | Add patient |
| `/patients/<id>/edit/` | Edit patient |
| `/appointments/` | Appointment list |
| `/appointments/create/` | New appointment |
| `/invoices/` | Invoice list |
| `/invoices/create/` | New invoice |
| `/invoices/<id>/` | Invoice detail |

## Production notes

- Set `DEBUG=False`, configure `ALLOWED_HOSTS`
- Use environment variables for secrets
- Run `python manage.py collectstatic`
- Deploy with Gunicorn + Nginx
